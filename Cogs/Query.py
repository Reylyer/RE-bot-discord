from typing import Optional, Any
import requests
import json, mariadb
from discord.ext import commands
from discord import File
import pprint
from itertools import chain, zip_longest


DATABASE_FILE = "Resource/databaseif.json"

class Query(commands.Cog):                  
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot: commands.Bot = bot
        self.database: dict = json.loads(open(DATABASE_FILE, 'r').read())

        try:
            self.conn: mariadb.Connection = mariadb.connect(
                user="mhs_querier",
                password="master_query",
                host="127.0.0.1",
                port=3306,
                database="mhs_query"
            )
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            

    @commands.command() #s-ping
    async def whois(self, ctx, nim):
        if nim in self.database:
            response = "```ps1\n"
            response += json.dumps(self.database[nim], indent=4)
            response += "```"
        else:
            response = f"Tidak menemukan mahasiswa dengan nim {nim}"
        await ctx.send(response)
    
    @commands.command()
    async def query(self, ctx: commands.context.Context, *, raw: str):
        expressions = raw.split(',')
        query_expressions = []
        for expression in expressions:
            column, like = expression.strip().split(':')
            query_expressions.append([column, like.strip(like[0])])
        selected = []
        for nim, info in self.database.items():
            info['nim'] = nim

            for column, like in query_expressions:
                if like not in info[column]:
                    break
            else:
                selected.append(info)

        if selected:
            response = json.dumps(selected, indent=4)
            try:
                await ctx.send("```json\n" + response + "\n```")
            except:
                f = open("query.json", "w")
                f.write(response)
                f.close()
                attachment = File("query.json")
                await ctx.send("enjoy~", file=attachment)
        else:    
            await ctx.send(raw)
    
    @commands.command(aliases=['eq', 'EXP_QUERY', 'EXPQUERY', 'EQ', 'EXPQ'])
    async def exp_query(self, ctx: commands.context.Context, *, qs: str):
        def create_string_table(li):
            s = [[str(e) for e in row] for row in li]
            lens = [max(map(len, col)) for col in zip(*s)]
            fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
            table = [fmt.format(*row) for row in s]
            return '\n'.join(table)

        cur = self.conn.cursor(buffered=True)
        try:
            atch = ctx.message.attachments
            if atch:
                qs = requests.get(atch[0].url).text
            print(qs)
            for q in qs.split(';'):
                q = q.strip()
                print("executing", q)
                cur.execute(q)
                if q.startswith(('INSERT', 'UPDATE')):
                    await ctx.send(f"`{cur.rowcount}` row(s) affected")
                else:
                    resq = []
                    if cur.rowcount:
                        resq.append([i[0] for i in cur.description])

                        for row in cur:
                            resq.append(list(map(str, row)))
                        result = create_string_table(resq)
                        try:
                            await ctx.send("```csv\n" + result + "\n```")
                        except:
                            f = open("query.csv", "w")
                            f.write(result)
                            f.close()
                            attachment = File("query.csv")
                            await ctx.send("enjoy~", file=attachment)
                    else:
                        await ctx.send(f"`{cur.rowcount}` row(s) returned")
        except mariadb.Error as e:
            await ctx.send(f"Error: {e}")
        cur.close()
