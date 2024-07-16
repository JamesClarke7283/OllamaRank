import os
from appdirs import user_data_dir
from tortoise import Tortoise
from tortoise.expressions import Q
from src.core.models import Model, Vote
from src.core.vote_outcome import VoteOutcome

class DatabaseManager:
    def __init__(self):
        self.db_path = os.path.join(user_data_dir("OllamaRank"), "local.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def init_db(self):
        await Tortoise.init(
            db_url=f"sqlite://{self.db_path}",
            modules={"models": ["src.core.models"]}
        )
        await Tortoise.generate_schemas()

    async def close_db(self):
        await Tortoise.close_connections()

    async def get_or_create_model(self, name, modelfile):
        model, created = await Model.get_or_create(
            name=name,
            defaults={"modelfile": modelfile}
        )
        if not created and model.modelfile != modelfile:
            model.modelfile = modelfile
            await model.save()
        return model

    async def record_vote(self, model_a_name, model_b_name, model_a_modelfile, model_b_modelfile, outcome):
        if not model_a_name or not model_b_name:
            raise ValueError("Model names must not be None")
        
        model_a = await self.get_or_create_model(model_a_name, model_a_modelfile or '')
        model_b = await self.get_or_create_model(model_b_name, model_b_modelfile or '')

        vote = await Vote.create(
            model_a=model_a,
            model_b=model_b,
            outcome=outcome
        )

        return vote

    async def get_leaderboard(self):
        models = await Model.all()
        leaderboard = []
        for model in models:
            wins = await Vote.filter(Q(model_a=model, outcome=VoteOutcome.WIN) | Q(model_b=model, outcome=VoteOutcome.LOSS)).count()
            losses = await Vote.filter(Q(model_a=model, outcome=VoteOutcome.LOSS) | Q(model_b=model, outcome=VoteOutcome.WIN)).count()
            ties = await Vote.filter(Q(model_a=model, outcome=VoteOutcome.TIE) | Q(model_b=model, outcome=VoteOutcome.TIE)).count()
            both_bad = await Vote.filter(Q(model_a=model, outcome=VoteOutcome.BOTH_BAD) | Q(model_b=model, outcome=VoteOutcome.BOTH_BAD)).count()
            total_votes = wins + losses + ties + both_bad
            if total_votes > 0:
                elo_rating = self.calculate_elo(wins, losses, ties)
                leaderboard.append({
                    'model': model,
                    'elo_rating': elo_rating,
                    'wins': wins,
                    'losses': losses,
                    'ties': ties,
                    'both_bad': both_bad,
                    'total_votes': total_votes
                })
        return sorted(leaderboard, key=lambda x: x['elo_rating'], reverse=True)

    def calculate_elo(self, wins, losses, ties):
        total_games = wins + losses + ties
        if total_games == 0:
            return 1500
        win_ratio = (wins + 0.5 * ties) / total_games
        return 1500 + 400 * (win_ratio - 0.5)

db_manager = DatabaseManager()
