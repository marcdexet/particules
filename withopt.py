import click

@click.command()
@click.option('--bounce', default=True, type=bool, help='Bounce.')
@click.option('--number_of_stars', default=1000, type=int, help='Number of stars.')
@click.option('--rand_ratio', default=0.001, type=float, help='Random ration.')
def run_my_game(bounce: bool, number_of_stars: int, rand_ratio: float):
    print(f'{bounce}, {number_of_stars}, {rand_ratio}')

if __name__ == '__main__':
    run_my_game()
