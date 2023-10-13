import pkg_resources  # type: ignore
import unified_planning as up  # type: ignore
from unified_planning.model import ProblemKind  # type: ignore
from unified_planning.engines import Engine, Credits, LogMessage  # type: ignore
from unified_planning.engines.mixins import OneshotPlannerMixin  # type: ignore
from typing import Callable, Dict, IO, List, Optional, Set, Union, cast  # type: ignore
from unified_planning.io.ma_pddl_writer import MAPDDLWriter  # type: ignore
import tempfile
import random
import json
import socket
import os
import sys
import asyncio
from unified_planning.exceptions import UPException
from unified_planning.engines.results import (
    LogMessage,
    PlanGenerationResult,
    PlanGenerationResultStatus,
)  # type: ignore
from unified_planning.model.multi_agent import MultiAgentProblem  # type: ignore
import re

credits = Credits(
    # Check and set ("name", "author" , "contact (for UP integration)", "website", "license", "short_description")
    "MA-BFWS",
    "Alfonso E. Gerevini, Nir Lipovetzky, Francesco Percassi, Alessandro Saetti and Ivan Serina",
    "ivan.serina@unibs.it",
    "MA-BFWS: Best-First Width Search for Multi Agent Privacy-Preserving Planning.",
    "...",
    "...",
    "...",
)

ma_bfws_os = {
    # 'win32':'maBFWS',
    "linux": "maBFWS"
}


class MA_BFWSsolver(Engine, OneshotPlannerMixin):
    def __init__(
        self, search_algorithm: Optional[str] = None, heuristic: Optional[str] = None
    ):
        Engine.__init__(self)
        OneshotPlannerMixin.__init__(self)
        self.search_algorithm = search_algorithm
        self.heuristic = heuristic

    @property
    def name(self) -> str:
        return "MA_BFWS"

    def _get_cmd_ma(
        self,
        problem: MultiAgentProblem,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
        agents_json: json,
        timeout: str,
    ):
        cmds = []
        directory = "ma_pddl_"
        if timeout is None:
            for ag in problem.agents:
                base_command = f"{pkg_resources.resource_filename(__name__, ma_bfws_os[sys.platform])} -o {directory}{domain_filename}{ag.name}_domain.pddl -f {directory}{problem_filename}{ag.name}_problem.pddl -n 1 -multiagent_list {directory}{agents_json}{ag.name}.json -out {plan_filename}/{ag.name}_plan.txt -multiagent_number_agents {len(problem.agents)} -noout -cputime 12000 -info_search 2"
                cmds.append(base_command)
        else:
            for ag in problem.agents:
                base_command = f"{pkg_resources.resource_filename(__name__, ma_bfws_os[sys.platform])} -o {directory}{domain_filename}{ag.name}_domain.pddl -f {directory}{problem_filename}{ag.name}_problem.pddl -n 1 -multiagent_list {directory}{agents_json}{ag.name}.json -out {plan_filename}/{ag.name}_plan.txt -multiagent_number_agents {len(problem.agents)} -noout -cputime {timeout} -info_search 2"
                cmds.append(base_command)
        return cmds

    def _result_status(
        self,
        problem: "up.model.multi_agent.MultiAgentProblem",
        plan: Optional["up.plans.Plan"],
        retval: int = 0,
        log_messages: Optional[List["LogMessage"]] = None,
    ) -> "PlanGenerationResultStatus":
        if retval != 0:
            return PlanGenerationResultStatus.INTERNAL_ERROR
        elif plan is None:
            return PlanGenerationResultStatus.UNSOLVABLE_PROVEN
        else:
            return PlanGenerationResultStatus.SOLVED_SATISFICING

    @staticmethod
    def supported_kind() -> "ProblemKind":
        """See unified_planning.model.problem_kind.py for more options """
        supported_kind = ProblemKind()
        supported_kind.set_problem_class("ACTION_BASED_MULTI_AGENT")
        supported_kind.set_numbers("CONTINUOUS_NUMBERS")  # type: ignore
        supported_kind.set_problem_type("SIMPLE_NUMERIC_PLANNING")  # type: ignore
        supported_kind.set_problem_type("GENERAL_NUMERIC_PLANNING")  # type: ignore
        supported_kind.set_typing("FLAT_TYPING")  # type: ignore
        supported_kind.set_typing("HIERARCHICAL_TYPING")  # type: ignore
        supported_kind.set_fluents_type("NUMERIC_FLUENTS")  # type: ignore
        supported_kind.set_conditions_kind("EQUALITIES")  # type: ignore
        supported_kind.set_numbers("DISCRETE_NUMBERS")  # type: ignore
        supported_kind.set_effects_kind("INCREASE_EFFECTS")  # type: ignore
        supported_kind.set_effects_kind("DECREASE_EFFECTS")  # type: ignore
        supported_kind.set_effects_kind(
            "STATIC_FLUENTS_IN_NUMERIC_ASSIGNMENTS"
        )  # type: ignore
        supported_kind.set_effects_kind(
            "FLUENTS_IN_NUMERIC_ASSIGNMENTS"
        )  # type: ignore
        supported_kind.set_time("CONTINUOUS_TIME")  # type: ignore
        supported_kind.set_quality_metrics("PLAN_LENGTH")  # type: ignore
        supported_kind.set_expression_duration(
            "STATIC_FLUENTS_IN_DURATIONS"
        )  # type: ignore
        supported_kind.set_actions_cost_kind(
            "STATIC_FLUENTS_IN_ACTIONS_COST"
        )  # type: ignore
        supported_kind.set_actions_cost_kind("FLUENTS_IN_ACTIONS_COST")  # type: ignore
        return supported_kind

    @staticmethod
    def supports(problem_kind: "ProblemKind") -> bool:
        return problem_kind <= MA_BFWSsolver.supported_kind()

    @staticmethod
    def get_credits(**kwargs) -> Optional["Credits"]:
        return credits

    def get_free_port(self, ip: str, n_port_min: int, n_port_max: int):
        while True:
            port = random.randint(n_port_min, n_port_max)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip, port))
            sock.close()
            if result != 0:
                return port

    def write_json(self, problem, json_dir):
        agent_ports = {}
        assigned_ports = set()
        ip = "127.0.0.1"
        n_port_min = 49152
        n_port_max = 65535
        outdir_json = "ma_pddl_" + json_dir
        os.makedirs(outdir_json, exist_ok=True)
        for agent in problem.agents:
            self_name = agent.name
            self_port = self.get_free_port(ip, n_port_min, n_port_max)
            agent_ports[self_name] = self_port
            assigned_ports.add(self_port)

        for ag in problem.agents:
            others = {}
            for other_ag in problem.agents:
                if other_ag.name != ag.name:
                    other_port = agent_ports[other_ag.name]
                    others[other_ag.name] = {
                        "communicate_to": [],
                        "communicate_from": [],
                        "address": f"tcp://{ip}:{other_port}",
                    }

            agent_json = {
                "self": {
                    "name": ag.name,
                    "address": f"tcp://{ip}:{agent_ports[ag.name]}",
                },
                "others": others,
            }

            filename = f"ma_pddl_{json_dir}{ag.name}.json"
            with open(filename, "w") as file:
                json.dump(agent_json, file, indent=4)

    def _solve(
        self,
        problem: "up.model.AbstractProblem",
        callback: Optional[
            Callable[["up.engines.results.PlanGenerationResult"], None]
        ] = None,
        heuristic: Optional[
            Callable[["up.model.state.ROState"], Optional[float]]
        ] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[IO[str]] = None,
    ) -> "up.engines.results.PlanGenerationResult":
        assert isinstance(problem, up.model.Problem) or isinstance(
            problem, up.model.multi_agent.MultiAgentProblem
        )
        logs: List["up.engines.results.LogMessage"] = []
        with tempfile.TemporaryDirectory() as tempdir:
            w = MAPDDLWriter(problem)
            domain_filename = os.path.join(tempdir, "domain_pddl/")
            problem_filename = os.path.join(tempdir, "problem_pddl/")
            json_filename = os.path.join(tempdir, "json/")
            plan_filename = os.path.join(f"ma_pddl_{tempdir}")
            self.write_json(problem, json_filename)
            w.write_ma_domain(domain_filename)
            w.write_ma_problem(problem_filename)
            cmds = self._get_cmd_ma(
                problem,
                domain_filename,
                problem_filename,
                plan_filename,
                json_filename,
                timeout,
            )
            loop = asyncio.get_event_loop()
            execs_res = loop.run_until_complete(self.exec_cmds(cmds, output_stream))
            for cmd in cmds:
                plan_filename = cmd.split("-out ")[1].split(" ")[0]
                log_filename = f"{plan_filename}.log"
                log_file = open(log_filename, "r")
                logs.append(log_file.read())
                log_file.close()
            for res in execs_res:
                if res[0] and res[1] != 0:
                    return PlanGenerationResult(
                        PlanGenerationResultStatus.TIMEOUT,
                        plan=None,
                        log_messages=logs,
                        engine_name=self.name,
                    )
            plans = dict()
            for cmd in cmds:
                plan_filename = cmd.split("-out ")[1].split(" ")[0]
                plans.update(
                    self._plan_from_file(problem, plan_filename, w.get_item_named)
                )

            if plans[-1]:
                type_of_plan = up.plans.TimeTriggeredPlan
            else:
                type_of_plan = up.plans.SequentialPlan
            plans.pop(-1)
            actions = []
            for i in range(len(plans.keys())):
                actions.append(plans[i])
            plan = type_of_plan(actions)
            status: PlanGenerationResultStatus = self._result_status(
                problem, plan, 0, logs
            )
            return PlanGenerationResult(
                status, plan, log_messages=logs, engine_name=self.name
            )

    def _plan_from_file(
        self,
        problem: "up.model.Problem",
        plan_filename: str,
        get_item_named: Callable[
            [str],
            Union[
                "up.model.Type",
                "up.model.Action",
                "up.model.Fluent",
                "up.model.Object",
                "up.model.Parameter",
                "up.model.Variable",
            ],
        ],
    ) -> "up.plans.Plan":
        """Takes a problem and a filename and returns the plan parsed from the file."""
        actions = []
        tt = False
        ordered_actions = dict()
        ordered_actions[-1] = False
        if "CONTINUOUS_TIME" in problem.kind.features:
            tt = True
            ordered_actions[-1] = True
        with open(plan_filename) as plan:
            for line in plan.readlines():
                if re.match(r"^\s*(;.*)?$", line):
                    continue
                res = re.match(
                    r"^[\s[\d.]+:\s*\(\s*([\w?-]+)((\s+[\w?-]+)*)\s*\)\s*$",
                    line.lower().split(" ;;")[0],
                )
                if res:
                    number_action = res.group(0).split(":")[0].replace(" ", "")
                    action = get_item_named(res.group(1))
                    parameters = []
                    for p in res.group(2).split():
                        p_correct = get_item_named(p)
                        if isinstance(p_correct, up.model.multi_agent.agent.Agent):
                            agent = p_correct
                        else:
                            parameters.append(
                                problem.environment.expression_manager.ObjectExp(
                                    p_correct
                                )
                            )
                    if tt:
                        start = re.match(r"^([\d.]+):", line).group(1)
                        dur = re.match(
                            r"^[\d.]+:\s*\(\s*[\w?-]+((\s+[\w?-]+)*)\s*\)\s*\[([\d.]+)\]$",
                            line,
                        ).group(3)
                        actions.append(
                            (
                                start,
                                up.plans.ActionInstance(action, tuple(parameters)),
                                dur,
                            )
                        )
                        ordered_actions[int(number_action)] = (
                            start,
                            up.plans.ActionInstance(action, tuple(parameters)),
                            dur,
                        )
                    else:
                        actions.append(
                            up.plans.ActionInstance(action, tuple(parameters), agent)
                        )
                        ordered_actions[int(number_action)] = up.plans.ActionInstance(
                            action, tuple(parameters), agent
                        )
                elif re.match(r"no solution", line):
                    return None
                else:
                    raise UPException(
                        "Error parsing plan generated by " + self.__class__.__name__
                    )
        return ordered_actions

    async def exec_async_cmd(self, cmd, output_stream):
        file_log = cmd.split("-out ")[1].split(" ")[0]
        if output_stream is None:
            output_stream = open(f"{file_log}.log", "a")
        process = await asyncio.create_subprocess_shell(cmd, stdout=output_stream)
        try:
            timeout_occurred = False
        except asyncio.TimeoutExpired:
            timeout_occurred = True
        await process.wait()
        return process.returncode, timeout_occurred

    async def exec_cmds(self, cmds, output_stream):
        tasks = [
            asyncio.create_task(self.exec_async_cmd(comando, output_stream))
            for comando in cmds
        ]
        return await asyncio.gather(*tasks)
