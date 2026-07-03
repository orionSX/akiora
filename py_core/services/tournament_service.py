from models.tournament import Tournament
from models.enums import Server, GameStatus, TournamentType
from models.vos import TournamentSettings
from uuid import UUID
from datetime import datetime


class TournamentService:
    async def get_by_id(self, id: str | UUID):
        return await Tournament.get(id)

    async def get_by_host(self, host_id: UUID):
        return await Tournament.find_many(Tournament.host_id == host_id).to_list()

    async def get_by_server(self, server: Server):
        return await Tournament.find_many(Tournament.server == server).to_list()

    async def get_by_status(self, status: GameStatus):
        return await Tournament.find_many(Tournament.status == status).to_list()

    async def create(self, host_id: UUID, patch: dict):
        ts = TournamentSettings(**patch)
        tournament = Tournament(
            host_id=host_id,
            name=ts.common_settings.name,
            server=ts.common_settings.server,
            tournament_type=ts.common_settings.tournament_type,
            starts_at=ts.common_settings.starts_at,
            description=ts.common_settings.description,
            prizepool=ts.common_settings.prizepool,
            team_size=ts.common_settings.team_size,
            team_max_count=ts.common_settings.team_max_count,
            draft_algorithm=ts.common_settings.draft_algorithm,
        )
        await tournament.save()
        return tournament
