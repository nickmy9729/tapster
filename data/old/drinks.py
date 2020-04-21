
drink_list = [{
                'name': 'Vesper',
                'ingredients': {
                        'gin': 60,
                        'vodka': 15.0,
                        'vermouth': 7.5
                },
                'steps': [
                        { 'pour': ['gin', 'vodka', 'vermouth'] },
                        { 'manual_step': 'Strain into a chilled cocktail glass.' },
                        { 'manual_step': 'Twist a slice of lemon peel over the drink, rub along the rim of the glass, and drop it in.' }
                ]
        }
]

drink_options = [
        {
                "name": "Gin",
                "value": "gin"
        },
        {
                "name": "White Rum",
                "value": "whiteRum"
        },
        {
                "name": "Dark Rum",
                "value": "darkRum"
        },
        {
                "name": "Coconut Rum",
                "value": "coconutRum"
        },
        {
                "name": "Vodka",
                "value": "vodka"
        },
        {
                "name": "Tequila",
                "value": "tequila"
        },
        {
                "name": "Tonic Water",
                "value": "tonic"
        },
        {
                "name": "Coke",
                "value": "coke"
        },
        {
                "name": "Orange Juice",
                "value": "oj"
        },
        {
                "name": "Margarita Mix",
                "value": "mmix"
        },
        {
                "name": "Cranberry Juice",
                "value": "cj"
        },
        {
                "name": "Pineapple Juice",
                "value": "pj"
        },
        {
                "name": "Apple Juice",
                "value": "aj"
        },
        {
                "name": "Grapefruit Juice",
                "value": "gj"
        },
        {
                "name": "Tomato Juice",
                "value": "tj"
        },
        {
                "name": "Lime Juice",
                "value": "lij"
        },
        {
                "name": "Lemon Juice",
                "value": "lej"
        },
        {
                "name": "Whiskey",
                "value": "whiskey"
        },
        {
                "name": "Triple Sec",
                "value": "tripSec"
        },
        {
                "name": "Grenadine",
                "value": "grenadine"
        },
        {
                "name": "Vermouth",
                "value": "vermouth"
        },
        {
                "name": "Soda",
                "value": "soda"
        },
        {
                "name": "Peach Schnapps",
                "value": "peachSchnapps"
        },
        {
                "name": "Midori",
                "value": "midori"
        },
        {
                "name": "Presecco",
                "value": "prosecco"
        },
        {
                "name": "Cherry Brandy",
                "value": "cherryBrandy"
        },
        {
                "name": "Apple Brandy",
                "value": "appleBrandy"
        },
        {
                "name": "Apricot Brandy",
                "value": "apricotBrandy"
        },
        {
                "name": "Brandy (generic)",
                "value": "brandy"
        },
        {
                "name": "Champagne",
                "value": "champagne"
        },
        {
                "name": "Cola",
                "value": "cola"
        },
        {
                "name": "Port",
                "value": "port"
        },
        {
                "name": "Coconut Milk",
                "value": "coconutMilk"
        },
        {
                "name": "Creme de Cacao",
                "value": "cremeCacao"
        },
        {
                "name": "Grenadine",
                "value": "grenadine"
        },
]
# Check for ingredients that we don 't have a record for
if __name__ == "__main__":
        found = []
        drinks = [x["value"] for x in drink_options]
        for D in drink_list:
                for I in D["ingredients"]:
                        if I not in drinks and I not in found:
                                found.append(I)
        print(I)
