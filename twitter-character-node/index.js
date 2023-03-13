const CharacterAI = require("node_characterai");

// Requiring fs module in which writeFile function is defined.
const fs = require("fs");
var util = require("util");

var log_file = fs.createWriteStream(__dirname + "/debug.log", { flags: "w" });
var log_stdout = process.stdout;

var logger = function (d) {
  log_file.write(util.format(d) + "\n");
  log_stdout.write(util.format(d) + "\n");
};

/**
 * Sleep so as to prevent rate limiting on character ai.
 * Sleep formula is s*(2^i) where s is some base amount of time in ms, 10 seconds to start.
 * @param {*} i - sleep iteration.
 */
async function sleep(i) {
  await new Promise((r) => setTimeout(r, 1000 * 2 ** i));
}

function randomListSelection(l) {
  if (l.length === 0) {
    return "";
  }
  return l[Math.floor(Math.random() * l.length)];
}

/**
 * Remove Pierre's actions from the tweet.
 * ex:
 *
 * My name is Pierre. *Pierre smokes* Bonjour.
 *  =>
 * My name is Pierre. Bonjour
 * @param {string} Tweet to clean
 * @returns tweet with action substrings removed.
 */
function removeActions(t) {
  let output = "";
  let add = true;
  let lastWasSpace = false;
  for (let i = 0; i < t.length; i++) {
    if (t[i] === "*") {
      add = !add;
    } else {
      if (lastWasSpace && t[i] === " ") {
      } else if (add) {
        output = output + t[i];

        if (t[i] === " ") {
          lastWasSpace = true;
        } else {
          lastWasSpace = false;
        }
      }
    }
  }
  return output.trim();
}

/**
 * Turn a paragraph into a list of sentences.
 * @param {*} t - input text
 * @returns Array of strings
 */
function getSentences(t) {
  return t.match(/([^\.!\?]+[\.!\?]+)|([^\.!\?]+$)/g);
}

/**
 * Choose up to n random, consecutive sentences.
 * @param {*} t - input text
 * @param {*} n - maximum number of sentences to return
 * @returns
 */
function chooseRandomSentences(t, n) {
  if (n <= 0) {
    return t;
  }
  const sentences = getSentences(t);
  const randomIndex = Math.floor(Math.random() * (sentences.length - 1));
  let result = "";
  for (let i = 0; i < n; i++) {
    if (randomIndex + i > sentences.length - 1) {
      return result;
    }

    result = result + sentences[randomIndex + i];
  }
  return result.trim();
}

/**
 * Gets a random prompt from the list of prompts to pass to pierre.
 * Within a prompt:
 * // n=0 means return full response.
 * // n>0 means return up to n sentences.
 * @returns Prompt instance with prompt and n values.
 */
async function getPrompt() {
  // try three times
  let prompts = null;
  for (let i = 0; i < 3; i++) {
    try {
      let promptsResponse = await fetch("http://sameermehra.com/assets/api/pierre-prompts.json");
      prompts = await promptsResponse.json();
      break;
    } catch (e) {
      if (!(e instanceof TypeError)) {
        throw e;
      }
      logger("Connection error, trying again...");
    }
  }
  const p = randomListSelection(prompts.prompts);
  logger(p);
  return p;
}

function writeToOutputFile(output) {
  // Data which will write in a file.
  let data = {};
  if (output) {
    data = { tweet: output };
  }

  // Write output. Since we are calling from parent directory, we include directory in path
  fs.writeFile("twitter-character-node/tweet_copy.json", JSON.stringify(data), (err) => {
    // In case of a error throw err.
    if (err) throw err;
  });
}

function charLimit(t) {
  // Twitter limit is 280, but prefer shorter tweets from Pierre.
  if (t.length <= 200) {
    return t;
  }
  return "";
}

/**
 * Filters the tweet, setting a character limit
 * @param {String} t - Tweet copy
 * @param {Object} p - prompt that resulted in the copy
 */
function filterTweet(t, p) {
  const t1 = removeActions(t);
  const t2 = chooseRandomSentences(t1, p.n);
  const t3 = charLimit(t2);
  return t3;
}

const characterAI = new CharacterAI();

async function talkToPierre() {
  await characterAI.authenticateAsGuest();

  // Pierre the Peanut
  const pierreId = "lDUsZaTzDTCFq9oj2dovbQwFE5gx0Yb2zYYuXO4UAbY";
  // Discord moderator
  const discordMod = "8_1NyR8w1dOXmI1uWaieQcd147hecbdIK7CeEAIrdJw";

  const chat = await characterAI.createOrContinueChat(pierreId);
  const prompt = await getPrompt();

  let output = "";
  for (let i = 0; i < 5; i++) {
    // get response
    // const response = await chat.sendAndAwaitResponse(prompt.prompt, true);
    const response = { text: "blah!" };

    logger("Full Response:\n");
    logger(response);
    logger("\n");
    logger("Selected Response:\n");
    output = filterTweet(response.text, prompt);
    logger(output);

    if (output) {
      break;
    }

    logger("Did not pass filtration steps, retrying...");

    sleep(i);
  }

  writeToOutputFile(output);
}

// Main
(async () => {
  talkToPierre();
})();
