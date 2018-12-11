"""This is Infin's text module.

It deals with manipulating text, such as with ciphers."""
import base64
import random
from Crypto.Cipher import AES
from Crypto.Cipher import XOR
from discord.ext import commands


def pad_for_aes(txt):
    """Pads the given text to properly support AES."""
    padded_portion = (AES.block_size - len(txt) % AES.block_size)
    return txt + padded_portion * \
        chr(AES.block_size - len(txt) % AES.block_size)


def unpad_for_aes(txt):
    """Unpads the given text to properly decode it."""
    return txt[:-ord(txt[len(txt) - 1:])]


class TextModule:
    """Contains commands that manipulate the given text."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='xorencrypt')
    async def xorencrypt(self, ctx, data, key):
        """Uses XOR to encipher the given text with the given key."""
        encryption = XOR.new(key)
        encrypted_data = base64.b64encode(
            encryption.encrypt(data)).decode('utf-8')
        await ctx.send(f':white_check_mark: **Encrypted data**: {encrypted_data}')

    @commands.command(name='xordecrypt')
    async def xordecrypt(self, ctx, data, key):
        """Uses XOR to decipher the given text with the given key."""
        encryption = XOR.new(key)
        decrypted_data = encryption.decrypt(
            base64.b64decode(data)).decode('utf-8')
        await ctx.send(f':white_check_mark: **Decrypted data**: {decrypted_data}')

    @commands.command(name='aesencrypt')
    async def aesencrypt(self, ctx, data, key):
        """Uses AES to encrypt the given text with the given key."""
        real_key = pad_for_aes(key)
        encryption = await self.bot.loop.run_in_executor(
            None, AES.new, real_key, AES.MODE_ECB)
        raw_encrypted_data = await self.bot.loop.run_in_executor(
            None, encryption.encrypt, pad_for_aes(data))
        encrypted_data = base64.b64encode(raw_encrypted_data).decode('utf-8')
        await ctx.send(f':white_check_mark: **Encrypted data**: {encrypted_data}')

    @commands.command(name='aesdecrypt')
    async def aesdecrypt(self, ctx, data, key):
        """Uses AES to decrypt the given text with the given key."""
        real_key = pad_for_aes(key)
        encryption = await self.bot.loop.run_in_executor(
            None, AES.new, real_key, AES.MODE_ECB)
        raw_decrypted_data = await self.bot.loop.run_in_executor(
            None, encryption.decrypt, base64.b64decode(data))
        decrypted_data = unpad_for_aes(raw_decrypted_data).decode('utf-8')
        await ctx.send(f':white_check_mark: **Decrypted data**: {decrypted_data}')

    @commands.command(name='shuffle')
    async def shuffle(self, ctx, *, data):
        """Shuffles the characters in the text at random."""
        data_array = list(data)
        random.shuffle(data_array)
        shuffled_data = ''.join(data_array)
        await ctx.send(f':white_check_mark: **Shuffled data**: {shuffled_data}')

    @commands.command(name='swapcase')
    async def swapcase(self, ctx, *, data):
        """Swaps the case of the given text."""
        swapped_case_data = data.swapcase()
        await ctx.send(f':white_check_mark: **Data with case swapped**: {swapped_case_data}')


def setup(bot):
    """Required to properly load the module into Infin."""
    bot.add_cog(TextModule(bot))
