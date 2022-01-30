const { channel } = require('diagnostics_channel');
const fs = require('fs');
const MOVIE = 0, TV = 1, RANDOM = 2;

function readWatchingListJSON(isolated, safe, type) {
    const userName = 'username';

    if (type === MOVIE) { } 
    else {
        const rawData = fs.readFileSync(`./profiles/${userName}Data/watchingListTV.json`);
        let watchingList = {};
        try { watchingList = JSON.parse(rawData); } catch (e) { }

        // Problem: 'The Office season 6'; if found in watching it will play season 6, with the up-next episode no matter the season
        if (isolated.season === -1) {
            try { isolated.season = watchingList[`${safe.content} (${safe.date})`].season; } 
            catch (e) { isolated.season = 1; }
        }
        
        if (isolated.episode === -1) {
            try { isolated.episode = watchingList[`${safe.content} (${safe.date})`].episode; } 
            catch (e) { isolated.episode = 1; }
        }
    }

    return {season: isolated.season, episode: isolated.episode }
}
  
function writeWatchingListJSON(data, safe, type) {
    // Maybe store contents url like this soap2day.sh/'EczoyMToiMTQ3MTR8fDUwLjEwMS4xNzEuMjIxIjs'.html;
    // Then it could go straight to the episode/movie
    // Could also store the next episodes url, and grab it in the background while the cast is initiating or something
    const userName = 'username';

    if (type === MOVIE) { } 
    else {
        const rawData = fs.readFileSync(`./profiles/${userName}Data/watchingListTV.json`);
        let watchingList = {};
        try { watchingList = JSON.parse(rawData); } catch (e) { }
        
        watchingList[`${safe.content} (${safe.date})`] = {};
        watchingList[`${safe.content} (${safe.date})`].season = data.season;
        watchingList[`${safe.content} (${safe.date})`].episode = data.episode;

        fs.writeFileSync(`./profiles/${userName}Data/watchingListTV.json`, JSON.stringify(watchingList));
    }
}

// check if the content asked to be played is in the watchlist; if so, delete from list.json
function readListJSON(safe, type) {
    const userName = 'username';

    if (type === MOVIE) { 
        const rawData = fs.readFileSync(`./profiles/${userName}Data/listMovie.json`);
        let list = [];
        try { list = JSON.parse(rawData); } catch (e) { }
        const index = Math.floor(Math.random() * list.length);
        const content = list[index].replace(/\(\d\d\d\d\)/g, '');
        
        list.splice(index, 1);
        fs.writeFileSync(`./profiles/${userName}Data/listMovie.json`, JSON.stringify(list));
        
        return { content: content, type: 'movie' }
    } 
    else if (type === TV) {
        const rawData = fs.readFileSync(`./profiles/${userName}Data/listTV.json`);
        let list = [];
        try { list = JSON.parse(rawData); } catch (e) { }
        const index = Math.floor(Math.random() * list.length);
        const content = list[index].replace(/\(\d\d\d\d\)/g, '');
        
        list.splice(index, 1);
        fs.writeFileSync(`./profiles/${userName}Data/listTV.json`, JSON.stringify(list));

        return { content: content, type: 'tv' }
    } 
    else if (type === RANDOM) {
        const type = Math.floor(Math.random() * 2) +1;
        const file = type === MOVIE ? 'Movie' : 'TV';
        const rawData = fs.readFileSync(`./profiles/${userName}Data/list${file}.json`);

        let list = [];
        try { list = JSON.parse(rawData); } catch (e) { }

        const index = Math.floor(Math.random() * list.length);
        const content = list[index].replace(/\(\d\d\d\d\)/g, '');
        
        list.splice(index, 1);
        fs.writeFileSync(`./profiles/${userName}Data/listTV.json`, JSON.stringify(list));

        let channelType = type === MOVIE ? 'movie' : 'tv';
        return { content: content, type: channelType }
    }
}

function writeListJSON(safe, type) {
    const userName = 'username';

    if (type === MOVIE) { 
        const rawData = fs.readFileSync(`./profiles/${userName}Data/listMovie.json`);
        let list = [];
        try { list = JSON.parse(rawData); } catch (e) { }
        list.push(`${safe.content} (${safe.date})`);

        fs.writeFileSync(`./profiles/${userName}Data/listMovie.json`, JSON.stringify(list));
    } 
    else if (type === TV) {        
        const rawData = fs.readFileSync(`./profiles/${userName}Data/listTV.json`);
        let list = [];
        try { list = JSON.parse(rawData); } catch (e) { }
        list.push(`${safe.content} (${safe.date})`);

        fs.writeFileSync(`./profiles/${userName}Data/listTV.json`, JSON.stringify(list));
    }
}

module.exports = { readWatchingListJSON, writeWatchingListJSON, readListJSON, writeListJSON };