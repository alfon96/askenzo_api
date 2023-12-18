from sqlalchemy.ext.automap import automap_base
import database

# initialize automap
Base = automap_base()
Base.prepare(autoload_with=database.engine)

Discovery = Base.classes.discoveries
Experiences = Base.classes.experiences
HostUser = Base.classes.host_users
TouristUser = Base.classes.tourist_users
TouristUserLikes = Base.classes.tourist_user_likes
PopupMsg = Base.classes.popup_msg
