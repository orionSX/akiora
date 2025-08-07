from models.data_managers import MongoManager, DragonManager
from models.user_service.User import User


class MongoUserManager(MongoManager[User]):
    _model_class = User


class DragonUserManager(DragonManager[User]):
    _model_class = User
