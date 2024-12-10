from Blog.models import User, Item, UserInventory

def run():
    nb_drop = 2
    nb_coins = 400
    users = User.objects.all()
    for user in users:
        user.coins += nb_coins
        user.save()
        for _ in range(nb_drop):
            UserInventory.objects.create(user=user, item=Item.objects.create(type='box'))

    print(f'{nb_drop} lootboxes dropped for each user | {nb_coins} coins added to each user')

if __name__ == '__main__':
    run()
