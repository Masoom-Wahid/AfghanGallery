from user_info.models import UserFavs, UserNotifications

def update_notifs(
        product : int,
        new_value: int,
        last_value : int,
        type_of : str
):
    if type_of == "vehicle":
        favs = UserFavs.objects.filter(
                vehicle=product
        )
    else:
        favs = UserFavs.objects.filter(
                real_estate=product
        )


    for fav in favs:
        if type_of == "vehicle":
            msg = f"{fav.vehicle} changed from {last_value} to {new_value}"
        else:
            msg = f"{fav.real_estate} changed from {last_value} to {new_value}"


        UserNotifications.objects.create(
            user = fav.user,
            fav=fav,
            msg=msg
        )

