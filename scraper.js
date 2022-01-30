const axios = require('axios');
const JSSoup = require('jssoup').default;
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth')
puppeteer.use(StealthPlugin())

const randomUserAgent = require('random-useragent');
const IMDB = 'https://www.imdb.com/find?q=';
const URL = ['https://soap2day.sh', 'https://s2dfree.to', 'https://s2dfree.is']; // https://soap2day.ac - subtitles are forbidden though axios
// Consider PhantomJS in the future;  only about 12MB instead of Puppeteers 300MB

// page.$ grabs element, page.$$ grabs elements --- page.$eval and page.$$eval accepts a filter function

const safeContent = (content) => { 
    if (content.includes(":")) { content = content.split(":")[1]; }
    if (content.includes(";")) { content = content.split(";")[1]; }
    if (content.includes(",")) { content = content.split(",")[1]; }
    return content.replace(/ /g, '%20')
}

const cleanContent = (content) => {
    return content.replace(/[.,\/#!$%\^&\*;:{}=\-_`~()]/g,"").replace(/\s/g,"").toLowerCase();
}

const enterSite = async (page) => {

    // Go directly to keyword search, then use entersite method, then go directlty to keyword again

    // Handles 503 server error by iterating through array of URLs until it works
    let index;
    for (let i = 0; i < URL.length; i++) {
        await page.goto(URL[i] + '/enter.html');
        try { await page.waitForSelector('h1', {timeout: 100}); } catch (e) { index = i; await page.waitForTimeout(200); break }
    }

    try {
        while (true) {
            if (!page.url().includes('enter.html')) {  break }
            await page.waitForNetworkIdle({ idleTime: 500});
            await page.waitForSelector('.btn-success', { timeout: 200,});
            await page.click('.btn-success');
        } 
    } catch (e) { }

    return index;
}

async function scrapeIMDB(content, date, type) {
    const link = IMDB + content.replace(/ /g, '%20') + '&s=tt&ttype=' + (type == 0 ? 'ft&ref_=fn_ft' : 'tv&ref_=fn_tv');
    const response = await axios.get(link).then((data => { return data.data; }));
    const soup = new JSSoup(response);
    const results = soup.findAll('td', 'result_text');

    for (let i = 0; i < results.length; i++) {
        const title = results[i].find('a').text;
        const cleanedIMDB = cleanContent(title); // Removes all punctuation and spaces to compare
        const cleanedContent = cleanContent(content);
        if (cleanedIMDB === cleanedContent) {
            if (date == -1) { date = results[i].text.match(/\d\d\d\d/g); }
            else if (!date.toString().includes(results[i].text.match(/\d\d\d\d/g))) { continue }
            return {content: title, date: date}
        }
    }

    return 'error'
}

async function scrapeUmmaTVUrl(content, date, season, episode, type) {
    // const response = await axios.get("https://www1.ummagurau.com/watch-tv/the-office-39383.4891918").then((data => { return data.data; }));

    //await page.waitForTimeout(100000);
    const browser = await puppeteer.launch( {headless: false});
    const page = await browser.newPage();

    const safe = await scrapeIMDB(content, date, type);
    content = safe.content;
    date = safe.date;

    await page.goto("https://www1.ummagurau.com/search/" + safe.content.replace(/ /g, "-").toLowerCase())
    await page.waitForSelector(".film-name", {timeout: 1000});
    let viable = []
    viable = await page.evaluate((content, date) => {
        const results = document.querySelectorAll("#main-wrapper > div > section > div.block_area-content.block_area-list.film_list.film_list-grid > div > div > div.film-detail.film-detail-fix > h2 > a");
        
        viable = []
        results.forEach((val) => {
            if (!val.innerText.includes(content)) { return }
            if (val.href.includes('tv')) { viable.push(val.href) }
        })

        return viable
    }, content, date, viable);

    for (let i = 0; i < viable.length; i++) {
        await page.goto(viable[i]);
        await page.waitForSelector(".film-poster", {timeout: 1000});
        const viableDate = await page.evaluate(() => {
            return document.querySelector("#main-wrapper > div.detail_page.detail_page-style > div.container > div.detail_page-watch > div.detail_page-infor > div > div.dp-i-c-right > div.elements > div > div.col-xl-5.col-lg-6.col-md-8.col-sm-12 > div:nth-child(1)").innerText
        });

        if (viableDate.includes(date.toString())) { break }
    }
    let link = []
    await page.evaluate((season, episode, link) => {
        document.querySelectorAll("#content-episodes > div > div.sl-content > div.slc-eps > div.sl-title > div > div > a")[season - 1].click()
    }, season, episode, link);

    await page.waitForTimeout(3000);
    link = await page.evaluate((episode, link) => {
        document.querySelectorAll(".active > ul > li > a").forEach((e) => { 
            if (e.innerText.includes(`Eps ${episode}:`)) { link = e.id }
        });
        return link
    }, episode, link)

    await page.click(`#${link}`)
    await page.waitForTimeout(3000);
    
    const elementHandle = await page.$('iframe');
    const frame = await elementHandle.contentFrame();

    while (true) {
        let html = await frame.evaluate(() => {

        })
    }

    while (true) {
        let val = await page.evaluate(() => {
            document.querySelector("#iframe-embed").src
        })
        console.log(val)
        await page.waitForTimeout(5000);
    }
    
    await page.waitForTimeout(300000000);


    console.log("URL: " + link)
    await page.goto(link);

    await page.waitForSelector(".film-poster", {timeout: 1000});
    await page.waitForTimeout(10000);
    


    await page.waitForTimeout(100000);
}

async function scrapeTVUrl(content, date, season, episode) {
    const browser = await puppeteer.launch( {args: ['--no-sandbox'], headless: true });
    const page = await browser.newPage();
    
    // const agent = randomUserAgent.getRandom(function (ua) { return ua.browserName === 'Firefox' && parseFloat(ua.browserVersion) >= 50; });

    // // console.log(agent)
    // await page.setUserAgent(agent);
    // await page.goto("https://bot.sannysoft.com/");
    // await page.waitForTimeout(1000000);

    const index = await enterSite(page);
    await page.goto(URL[index] + '/search/keyword/' + safeContent(content));
    try { await page.waitForSelector('.thumbnail', {timeout: 200}); } 
    catch (e) { }

    await page.evaluate((content, date) => {
        const results = document.querySelectorAll("body > div > div:nth-child(3) > div > div.col-sm-8.col-lg-8.col-xs-12 > div:nth-child(2) > div.panel-body > div > div > div > div > div > div")
        
        for (let i = 0; i < results.length; i++) {
            if (!results[i].innerText.includes(content)) { continue; }
            if (results[i].innerText.includes(date.toString())) { } // Date might be a mismatch with IMDB date
            else if (results[i].innerText.includes((date +1).toString())) { }
            else if (results[i].innerText.includes((date -1).toString())) { continue; }

            document.querySelector(`body > div > div:nth-child(3) > div > div.col-sm-8.col-lg-8.col-xs-12 > div:nth-child(2) > div.panel-body > div > div > div > div > div:nth-child(1) > div:nth-child(${i + 2}) > div > div:nth-child(2) > h5 > a:nth-child(1)`).click()
            break
        }
    }, content, date);

    console.log(page.url());
    await page.waitForNetworkIdle({ idleTime: 300});
    const listing = await page.evaluate((season, episode) => {
        thumbnail = document.querySelector("body > div > div:nth-child(3) > div > div.col-sm-8 > div:nth-child(1) > div > div > div > div.col-md-5.col-lg-5.visible-md.visible-lg > div > div > img").src
        
        const index = Array.from(document.querySelectorAll("body > div > div:nth-child(3) > div > div.col-sm-8 > div:nth-child(1) > div > div > div > div.col-sm-12.col-lg-12 > div")).findIndex(v => v.innerText.includes(`${season} :`))
        const episodes = document.querySelectorAll(`body > div > div:nth-child(3) > div > div.col-sm-8 > div:nth-child(1) > div > div > div > div.col-sm-12.col-lg-12 > div:nth-child(${index + 2}) > div > div > a`);

        for (let i = 0; i < episodes.length; i++) {
            if (episode == episodes[i].innerText.split(".")[0]) { 
                if (episode + 1 > episodes.length) {
                    season += 1;
                    episode = 1;
                } else { episode += 1; }
                episodes[i].click(); 

                return { season: season, episode: episode, thumbnail: thumbnail }
            }
        }
    }, season, episode);

    await page.tracing.start();
    await page.waitForSelector('.panel-player' );

    try { await page.waitForNetworkIdle({timeout: 2500}); } catch (e) {}
    let tracing = JSON.parse(await page.tracing.stop()); 
    // let responses = tracing.traceEvents.filter(te => te.name === "ResourceRecieveRequest")
    const responses = tracing.traceEvents
    let video, subtitle;

    responses.forEach((val) => {
        try {
            temp = val['args']['data']['url'];
            if (temp.includes('.mp4')) { video = temp }
            else if (temp.includes('English.srt')) { subtitle = temp }
        } catch(e) {}
    })
    return { season: listing.season, episode: listing.episode, videoUrl: video, subtitleUrl: subtitle, thumbnailUrl: listing.thumbnail }
};

async function scrapeMovieURL(content, date) {
    const browser = await puppeteer.launch( {headless: true});
    const page = await browser.newPage();

    const index = await enterSite(page);
    await page.goto(URL[index] + '/search/keyword/' + safeContent(content));
    await page.waitForSelector('.thumbnail');

    await page.evaluate((content, date) => {
        const results = document.querySelectorAll("body > div > div:nth-child(3) > div > div.col-sm-8.col-lg-8.col-xs-12 > div:nth-child(1) > div.panel-body > div > div > div > div > div > div")

        for (let i = 0; i < results.length; i++) {
            if (!results[i].innerText.includes(content)) { continue; }
            if (results[i].innerText.includes(date.toString())) { } // Date might be a mismatch with IMDB date
            else if (results[i].innerText.includes((date +1).toString())) { }
            else if (results[i].innerText.includes((date -1).toString())) { continue; }

            document.querySelector(`body > div > div:nth-child(3) > div > div.col-sm-8.col-lg-8.col-xs-12 > div:nth-child(1) > div.panel-body > div > div > div > div > div:nth-child(1) > div:nth-child(${i + 2}) > div > div:nth-child(2) > h5 > a:nth-child(1)`).click()
        }
    }, content, date);

    await page.tracing.start( )
    await page.waitForSelector('.panel-player' );

    const thumbnail = await page.evaluate(() => {
        return document.querySelector("body > div > div:nth-child(3) > div > div.col-sm-8 > div:nth-child(1) > div > div > div > div.col-md-5.col-lg-5.visible-md.visible-lg > div > div > img").src
    })

    try {await page.waitForNetworkIdle({timeout: 2500});} catch(e) {}
    let tracing = JSON.parse(await page.tracing.stop()); 
    // let responses = tracing.traceEvents.filter(te => te.name === "ResourceRecieveRequest")
    const responses = tracing.traceEvents
    let video, subtitle;
    responses.forEach((val) => {
        try {
            if (val['args']['data']['url'].includes("mp4")) {
                video = val['args']['data']['url']
            } else if (val['args']['data']['url'].includes("English.srt")) {
                subtitle = val['args']['data']['url']
            }
        } catch(e) {}
    })

    return { videoUrl: video, subtitleUrl: subtitle, thumbnailUrl: thumbnail }
}

async function scrapeSubtitles(url) {
    try { return await axios.get(url).then((data => { return data.data; })); } catch (e) { return false}
}

module.exports = { scrapeIMDB, scrapeTVUrl, scrapeMovieURL, scrapeSubtitles, scrapeUmmaTVUrl };