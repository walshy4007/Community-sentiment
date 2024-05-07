import sqlite3
import discord
from discord.ext import commands

DATABASE_PATH = 'sentiments.db'

class RoleCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="add_role", description="Add a role to the list of roles allowed to use restricted commands.")
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx, role: discord.Role):
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO allowed_roles (guild_id, role_id) VALUES (?, ?)',
                      (str(ctx.guild.id), str(role.id)))
            conn.commit()
        await ctx.respond(f"Role {role.name} has been added to the allowed list.", ephemeral=True)

    @commands.slash_command(name="remove_role", description="Remove a role from the list of roles allowed to use restricted commands.")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, role: discord.Role):
        with sqlite3.connect(DATABASE_PATH) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM allowed_roles WHERE guild_id = ? AND role_id = ?',
                      (str(ctx.guild.id), str(role.id)))
            conn.commit()
        await ctx.respond(f"Role {role.name} has been removed from the allowed list.", ephemeral=True)

def setup(bot):
    bot.add_cog(RoleCommands(bot))
