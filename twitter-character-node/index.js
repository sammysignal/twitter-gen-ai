const CharacterAI = require("node_characterai");

// Requiring fs module in which writeFile function is defined.
const fs = require("fs");

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
      console.log("Connection error, trying again...");
    }
  }
  const p = randomListSelection(prompts.prompts);
  console.log(p);
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
  if (t.length <= 280) {
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
  console.log(t);
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
  for (let i = 0; i < 3; i++) {
    const response = await chat.sendAndAwaitResponse(prompt.prompt, true);

    console.log("Full Response:\n");
    console.log(response);

    console.log("Selected Response:\n");
    output = filterTweet(response.text, prompt);
    console.log(output);

    if (output) {
      break;
    }

    console.log("Did not pass filtration steps, retrying...");
  }

  writeToOutputFile(output);
}

// Main
(async () => {
  talkToPierre();
})();
