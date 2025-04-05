import discord
from discord.ext import commands
import os
TOKEN = os.getenv("token")

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

CHANNEL_ID = 1357921147798294792  # ID kênh cố định


class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(
                label="Verify Role",
                style=discord.ButtonStyle.link,  # Chuyển sang kiểu link button
                emoji="✅",
                url="https://restorecord.com/verify/Maous%20Store%20%7C%20Verify"  # Thay link này bằng link của bạn
            )
        )



@bot.event
async def on_ready():
    print(f"Bot {bot.user} đã sẵn sàng!")

    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        async for message in channel.history(limit=10):  # Kiểm tra 10 tin nhắn gần nhất để tránh gửi trùng
            if message.author == bot.user and message.embeds:
                return  # Nếu đã có embed, không gửi lại

        embed = discord.Embed(
            title="Welcome To Maous Store",
            description="Việc Verify sẽ giúp nếu server có vấn đề bạn sẽ được **auto mời sang 1 server mới của Store**",
            color=discord.Color.dark_red()
        )

        embed.add_field(
            name="HƯỚNG DẪN NHẬN ROLE",
            value=(
                ">>> **Bước 1:** Ấn vào nút 'Verify Role' bên dưới\n"
                "**Bước 2:** Sau khi hiện lên bảng 'Ủy Quyền'\n"
                "**Bước 3:** Bạn ấn phê duyệt, bot sẽ mở ra website\n\n"
            ),
            inline=False
        )

        embed.set_footer(
            text="Maous Store • 2025",
            icon_url="https://img.upanh.tv/2025/04/05/88f30fd98515be8ccd42d0d289ee173ee0d53b2a28c604b904461477778149ae---Copy.png"
        )

        view = VerifyButton()
        await channel.send(embed=embed, view=view)  # Gửi vào kênh cố định


bot.run(TOKEN)
