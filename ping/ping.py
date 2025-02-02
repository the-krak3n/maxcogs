# Thanks preda for shards and fixator10 for editing most things.
# Thanks Senroht#5179 for permissions to use his code here.
import time
from typing import Optional

import discord
from redbot.core import Config, commands
from redbot.core.utils import chat_formatting as chat
from redbot.core.utils.chat_formatting import box

old_ping = None


class Ping(commands.Cog):
    """Reply with [botname]'s latency."""

    __author__ = "MAX, Senroht#5179, Fixator10, Preda"
    __version__ = "0.0.6"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad!"""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nAuthor: {self.__author__}\nCog Version: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=12435434124)
        self.config.register_global(
            def_msg="Pong !",
        )

    def cog_unload(self):
        global old_ping
        if old_ping:
            try:
                self.bot.remove_command("ping")
            except:
                pass
            self.bot.add_command(old_ping)

    @commands.is_owner()
    @commands.group(aliases=["setping"])
    async def pingset(self, ctx):
        """Settings to change ping title shown in the embed."""

    @pingset.command(name="set", aliases=["add"], usage="<message>")
    async def pingset_set(self, ctx, *, message: str):
        """Change the message for your ping title.

        You cannot have longer than 2000 on `<message>`.

        **Example:**
        - `[p]pingset set ping pong!`

        **Arguments:**
        - `<message>` is where you set your message.
        """
        if len(message) > 2000:
            return await ctx.send("Your message must be 2000 or fewer in length.")
        if message:
            await self.config.def_msg.set(message)
            await ctx.send(
                f"\N{WHITE HEAVY CHECK MARK} Sucessfully set the ping message to `{message}`."
            )

    @pingset.command(name="reset")
    async def pingset_reset(self, ctx):
        """Reset the ping message back to default."""
        await self.config.def_msg.clear()
        await ctx.send(
            "\N{WHITE HEAVY CHECK MARK} Sucessfully reset the ping message to default."
        )

    @commands.command(name="ping")
    @commands.bot_has_permissions(embed_links=True)
    async def _ping(self, ctx, show_shards: Optional[bool] = None):
        """Reply with [botname]'s latency.

        This does not matter if your ping is not above 300ms.

        - Discord WS: Websocket latency.
        - Message: Difference between your command's timestamp and the bot's reply's timestamp.
        - Time: Time it takes for the bot to send a message.
        """
        show_shards = (
            len(self.bot.latencies) > 1 if show_shards is None else show_shards
        )
        latency = self.bot.latency * 1000
        if show_shards:

            shards = [
                ("Shard {}/{}: {}ms").format(
                    shard + 1, self.bot.shard_count, round(pingt * 1000)
                )
                for shard, pingt in self.bot.latencies
            ]
        emb = discord.Embed(
            title=(await self.config.def_msg()),
            color=discord.Color.red(),
        )
        emb.add_field(
            name="Discord WS:",
            value=chat.box(str(round(latency)) + "ms", "yaml"),
        )
        emb.add_field(name=("Message:"), value=chat.box("…", "yaml"))
        emb.add_field(name=("Typing:"), value=chat.box("…", "yaml"))

        if show_shards:
            emb.add_field(name=("Shards:"), value=chat.box("\n".join(shards), "yaml"))

        before = time.monotonic()
        message = await ctx.send(embed=emb)
        ping = (time.monotonic() - before) * 1000

        emb.colour = await ctx.embed_color()
        emb.set_field_at(
            1,
            name=("Message:"),
            value=chat.box(
                str(
                    int(
                        (
                            message.created_at
                            - (ctx.message.edited_at or ctx.message.created_at)
                        ).total_seconds()
                        * 1000
                    )
                )
                + "ms",
                "yaml",
            ),
        )
        emb.set_field_at(
            2, name=("Typing:"), value=chat.box(str(round(ping)) + "ms", "yaml")
        )

        await message.edit(embed=emb)


def setup(bot):
    ping = Ping(bot)
    global old_ping
    old_ping = bot.get_command("ping")
    if old_ping:
        bot.remove_command(old_ping.name)
    bot.add_cog(ping)
