const Scraper = require('./scraper');
const FileSystem = require('./fileSystem');
const MOVIE = 0, TV = 1, RANDOM = 2;

const CommandList = ['watch list', 'shuffle', 'init', 'view']

// Add a command to view what's on the watchlist in Discord as a list
async function addToWatchlist(isolated) {
    if (isolated.content.includes('tv')) { isolated = { content: isolated.content.replace('tv', ''), date: isolated.date, type: TV } }
    else if (isolated.content.includes('movie')) { isolated = { content: isolated.content.replace('movie', ''), date: isolated.date, type: MOVIE } }
    else { isolated = { content: isolated.content, date: isolated.date, type: TV } } // Default to TV

    const safe = await Scraper.scrapeIMDB(isolated.content, isolated.date, isolated.type);
    FileSystem.writeListJSON(safe, isolated.type);
    return -1;
}

async function shufflePlay(message) {
    const type = message.includes('movie') ? MOVIE : message.includes('tv') ? TV : RANDOM;
    const jsonList = "tv";

    const response = FileSystem.readListJSON(jsonList, type);
    const result = `!stream ${response.content}`;
    return { channel: response.type, message: result }
}

// Will create a new folder with specified name, and fresh .json files for that profile
function initProfile(name, chromecast) {
    return 0;
}

async function commandFilter(isolated) {
    let command;
    for (let i = 0; i < CommandList.length; i++) { if (isolated.content.includes(CommandList[i])) { command = i; break } }
    isolated.content = isolated.content.replace(CommandList[command], '');
    
    if (CommandList[command] === 'watch list') { return await addToWatchlist(isolated) }
    if (CommandList[command] === 'shuffle') { return await shufflePlay(isolated.content) }
}

module.exports = { commandFilter };