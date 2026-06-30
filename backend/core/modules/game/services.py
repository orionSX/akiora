from typing import Any
from uuid import UUID

from modules.community.models import Host
from modules.game.enums import TournamentType
from modules.game.models.tournament import Tournament
from modules.game.value_objects.single_elim_bracket import SingleElim
from modules.utils import time_now


class TournamentService:
    async def list_tournaments(self) -> list[Tournament]:
        return await Tournament.find_all().sort(-Tournament.created_at).to_list()

    async def get_by_id(self, tournament_id: str | UUID) -> Tournament | None:
        return await Tournament.get(tournament_id)

    async def create_tournament(self, owner_id: str | UUID, payload: dict[str, Any]) -> Tournament:
        host_id = payload.get("host_id")
        if not host_id:
            raise ValueError("host_id is required")

        host = await Host.get(host_id)
        if not host:
            raise LookupError("Host not found")

        if str(host.owner_id) != str(owner_id):
            raise PermissionError("You can create tournaments only for your own host")

        tournament = Tournament(**payload)
        await tournament.insert()
        return tournament

    async def update_tournament(
        self, tournament_id: str | UUID, owner_id: str | UUID, patch: dict[str, Any]
    ) -> Tournament | None:
        tournament = await Tournament.get(tournament_id)
        if not tournament:
            return None

        host = await Host.get(tournament.host_id)
        if not host:
            raise LookupError("Host not found")
        if str(host.owner_id) != str(owner_id):
            raise PermissionError("You can update tournaments only for your own host")

        for field in (
            "name",
            "description",
            "server",
            "tournament_type",
            "status",
            "prizepool",
            "start_time",
            "team_size",
            "team_max_count",
            "draft_algorithm",
            "bracket",
        ):
            if field in patch:
                setattr(tournament, field, patch[field])

        tournament.updated_at = time_now()
        await tournament.save()
        return tournament

    async def generate_single_elim_bracket(
        self, tournament_id: str | UUID, owner_id: str | UUID, team_ids: list[UUID]
    ) -> Tournament | None:
        tournament = await Tournament.get(tournament_id)
        if not tournament:
            return None

        host = await Host.get(tournament.host_id)
        if not host:
            raise LookupError("Host not found")
        if str(host.owner_id) != str(owner_id):
            raise PermissionError("You can update tournaments only for your own host")

        if tournament.tournament_type != TournamentType.PRESIGN:
            raise ValueError("Single elimination bracket generation is available only for presign tournaments")

        bracket = SingleElim(teams=team_ids)
        flat_matches = bracket.build_bracket()
        tournament.bracket = {
            "format": "single_elimination",
            "matches": [match.model_dump(mode="json") for match in flat_matches],
        }
        tournament.updated_at = time_now()
        await tournament.save()
        return tournament
