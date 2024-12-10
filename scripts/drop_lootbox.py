from Blog.models import User, Item, UserInventory, Box
import argparse

def run(*args):
    parser = argparse.ArgumentParser()
    parser.add_argument('nb_drop', type=int)
    parser.add_argument('nb_coins', type=int)
    args = parser.parse_args(args)

    users = User.objects.all()
    box_id = Box.objects.last().id
    for user in users:
        user.coins += args.nb_coins
        user.save()
        for _ in range(args.nb_drop):
            UserInventory.objects.create(user=user, item=Item.objects.create(type='box', item_id=box_id))

    print(f'{args.nb_drop} lootboxes dropped for each user | {args.nb_coins} coins added to each user')


