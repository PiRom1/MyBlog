from Blog.models import User, Item, UserInventory, Box
import argparse

def run():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--nb_drop', type=int, default=2)
    # parser.add_argument('--nb_coins', type=int, default=400)
    # args = parser.parse_args(args)
    nb_drop = 2
    nb_coins = 400

    users = User.objects.all()
    box_id = Box.objects.last().id
    for user in users:
        user.coins += nb_coins
        user.save()
        for _ in range(nb_drop):
            UserInventory.objects.create(user=user, item=Item.objects.create(type='box', item_id=box_id))

    print(f'{nb_drop} lootboxes dropped for each user | {nb_coins} coins added to each user')


