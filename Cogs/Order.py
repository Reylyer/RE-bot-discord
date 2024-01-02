import json
from discord.ext import commands
from discord.ext.commands.context import Context
from os.path import exists
import os
from datetime import date

ORDER_HISTORY_FOLDER = "Resource/Order/order_histories/"
MENUS_FILE = "Resource/Order/menus.json"
# there is order_history and menus file

"""
menus.json structure
{
    "restaurant1" : {
        "menu1" : {
            "price": price,
            "details": "bla bla bla",
        },
        "menu2" : {
            "price": price,
            "details": "bla bla bla",
        },
    }, 
    "restaurant2" : {
        ...
    },
}

order.json
{
    "date" : date,
    "menu" : menu,
    "orders" : {
        "cust1": {
            "menu1": amo,
            "menu2": amo,
        }
    }
}

"""

class Order(commands.Cog):                  
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot

        # basic check file and folder
        if not exists(ORDER_HISTORY_FOLDER):
            os.makedirs(ORDER_HISTORY_FOLDER, exist_ok=True)
        if not exists(MENUS_FILE):
            with open(MENUS_FILE, 'w') as f:
                f.write("{}")

        self.menus: dict[str, dict] = json.loads(open(MENUS_FILE , 'r').read())
        self.active_order = {}

    @commands.command()
    async def create_menu(self, ctx: Context, menu_name: str):
        if menu_name in self.menus:
            await ctx.send(f"Menu {menu_name} sudah terdaftar")
            await ctx.invoke(self.show_menu, menu_name)
        else:
            self.menus[menu_name] = {}
            self.save_menu()
            await ctx.send(f"Menu {menu_name} terdaftar")
    
    @commands.command()
    async def add_menu_entry(self, ctx: Context, menu_name: str, *, entry):
        if menu_name in self.menus:
            entry = entry.split()
            if len(entry) > 1:
                entry_name, price = " ".join(entry[:len(entry)-1]), entry[-1]
                menu = self.menus[menu_name]
                menu[entry_name] = {
                    "price": int(price),
                    "details": ''
                }

                self.save_menu()
                await ctx.send(f"Entry {entry_name} ditambahkan ke {menu_name}")
                await ctx.invoke(self.show_menu, menu_name)
                # await ctx.send(f"Format salah {e}")
        else:
            self.menus[menu_name] = {}
            self.save_menu()
            await ctx.send(f"Menu {menu_name} terdaftar")

    @commands.command()
    async def delete_menu(self, ctx: Context, menu_name: str):
        if menu_name in self.menus:
            self.menus.pop(menu_name)
            await ctx.send(f"Menu {menu_name} sudah terhapus")
            self.save_menu()
        else:
            await ctx.send(f"Menu {menu_name} belum terdaftar")

    @commands.command()
    async def show_menu(self, ctx: Context, menu_name: str):
        if menu_name in self.menus:
            if self.menus[menu_name]:
                
                await ctx.send(f"{menu_name}\n\n```js\n" + "\n".join([f"{i}\t{fd}:\t{det['price']}\n\t{det['details']}" for i, (fd, det) in enumerate(self.menus[menu_name].items())]) + "```")
            else:
                await ctx.send(f"Menu {menu_name} masih kosong")
        else:
            await ctx.send(f"Menu {menu_name} belum terdaftar")

    def save_menu(self):
        with open(MENUS_FILE, 'w') as f:
            f.write(json.dumps(self.menus, indent=4))

    @commands.command()
    async def create_order(self, ctx: Context, menu_name: str):
        if menu_name in self.menus:
            if self.active_order:
                await ctx.invoke(self.archive_order)
            self.active_order['date'] = date.today().strftime("%d-%m-%Y")
            self.active_order['menu'] = menu_name
            self.active_order['orders'] = {}
        else:
            await ctx.send(f"Menu {menu_name} tidak terdaftar")

    @commands.command()
    async def order(self, ctx: Context, num: str, amo: str):
        if self.active_order:
            active_menu = self.menus[self.active_order['menu']]
            if int(num) < len(active_menu.keys()):
                order_menu = active_menu[list(active_menu.keys())[int(num)]]
                self.active_order['orders'][ctx.author][order_menu] = int(amo)
                await ctx.invoke(self.show_summary)
            else:
                await ctx.send("Out of range")
                await ctx.invoke(self.show_menu, active_menu['menu'])
        else:
            await ctx.send("Belum ada order yang dibuat")

    @commands.command()
    async def cancel(self, ctx: Context, num: str):
        await ctx.send("not implemented yet")
    
    @commands.command()
    async def show_summary(self, ctx: Context):
        if self.active_order:
            summary = {}
            response = self.active_order['menu'] +'-'+ self.active_order['date'] + "\n\n"
            response+= "orders:\n"
            response+= "```js\n"
            for cust, _orders in self.active_order['orders']:
                response += cust + "\n"
                mini_sum = 0
                for menu, amount in _orders:
                    mini_sum += self.menus[self.active_order['menu']][menu]['price']*amount
                    response += f"\t{menu} {amount}\n"
                    if menu in summary:
                        summary[menu] = amount
                    else:
                        summary[menu]+= amount
                response += "bill: {:,}\n\n".format(mini_sum)
            
            response+= "total:\n"
            total_sum = 0
            for menu, amount in summary:
                mini_sum = self.menus[self.active_order['menu']][menu]['price']*amount
                response+= f"\t {menu} {amount}: " + "{:,}\n".format(mini_sum)
                total_sum+= mini_sum
            response += "\ntotal: {:,}\n".format(total_sum)
            response += "```"
            await ctx.send(response)


    @commands.command()
    async def archive_order(self, ctx: Context):
        await ctx.send(f"Archiving {self.active_order['date']}")
        with open(ORDER_HISTORY_FOLDER + self.active_order['menu'] +'-'+ self.active_order['date'], 'w') as f:
            f.write(json.dumps(self.active_order, indent=4))
        self.active_order = {}
        
    



