const { spawn } = require('child_process');

const Discord = require('discord.js');
const { Client, Intents } = require('discord.js');

const client = new Client({ intents: [Intents.FLAGS.GUILDS, Intents.FLAGS.GUILD_MESSAGES] });

const prefix = '!';

// Providers
// const providers = {
//     0: "ummagurau.py", 
//     1: "soap2day.py"
// }

let providerCount = 2
let provider = 1

client.once('ready', (bot) => {
    console.log('Streamer is active.')
    client.user.setActivity("");
});

client.on('messageCreate', message => {
    if (!message.content.startsWith(prefix)) { return}
    type = message.channel.name === "stream-movie" ? 0 : 1

    const args = message.content.slice(prefix.length).split(/ +/);
    const command = args.shift().toLowerCase();
    console.log(args)
    let content = args.join(" ")

    if (command === 'stream' && !content.includes("cancel")) {
        // python3 for mac; python for windows
        const pythonScript = spawn('python3', ['main.py', content, provider, type]);

        client.user.setActivity(content.split(",")[0]);

        pythonScript.stderr.on('data', (data) => {
            console.log(data)
        });

        pythonScript.stdout.on('data', (data) => {
            console.log(data.toString())
        });
    } else if (command == 'switch' && !content.includes("cancel")) {
        provider = ++provider % providerCount  
    }
});

client.login('OTE3NTU4NDgyMjY0MjY4ODcw.Ya6c7Q.zpHX6wYRCGOv38gnq_6u4UpBUF0');