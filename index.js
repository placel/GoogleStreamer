const { spawn } = require('child_process');

const Discord = require('discord.js');
const { Client, Intents } = require('discord.js');

const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });

const prefix = '!';

client.once('ready', () => {
    console.log('Bot is active.')
});

client.on('message', message => {
    if (!message.content.startsWith(prefix)) { return}

    const args = message.content.slice(prefix.length).split(/ +/);
    const command = args.shift().toLowerCase();
    console.log(args)
    let content = args.join(" ")

    if (command === 'stream') {
        message.channel.send('Casting ' + content);
        const pythonScript = spawn('python3', ['main.py', content]);

        pythonScript.stderr.on('data', (data) => {
            console.log(data)
        });

        pythonScript.stdout.on('data', (data) => {
            console.log(data.toString())
        });
        
        pythonScript.stdin.on('data', (data) => {
            console.log(data.toString())
        });

    }
});

client.login('OTE3NTU4NDgyMjY0MjY4ODcw.Ya6c7Q.zpHX6wYRCGOv38gnq_6u4UpBUF0');