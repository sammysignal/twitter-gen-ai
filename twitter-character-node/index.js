const CharacterAI = require("node_characterai");

// Requiring fs module in which writeFile function is defined.
const fs = require("fs");

// n=0 means return full response.
// n>0 means return up to n sentences.
PROMPTS = [
  {
    prompt: "What are you doing?",
    n: 0,
  },
  {
    prompt: "Where did you go?",
    n: 0,
  },
  {
    prompt: "You say the strangest things.",
    n: 0,
  },
  {
    prompt: "What's on your mind?",
    n: 2,
  },
  {
    prompt: "What happens in France?",
    n: 2,
  },
  {
    prompt: "You are very cool!",
    n: 2,
  },
  {
    prompt: "Do you have any fun date ideas?",
    n: 1,
  },
  {
    prompt: "Do you have any fun date ideas?",
    n: 1,
  },
];

function randomListSelection(l) {
  if (l.length === 0) {
    return "";
  }
  // return l[Math.floor(Math.random() * l.length)];
  return l[3];
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
 * @returns String
 */
function getPrompt() {
  const p = randomListSelection(PROMPTS);
  console.log(p);
  return p;
}

function writeToOutputFile(output) {
  // Data which will write in a file.
  let data = { tweet: output };

  // Write output. Since we are calling from parent directory, we include directory in path
  fs.writeFile("twitter-character-node/tweet_copy.json", JSON.stringify(data), (err) => {
    // In case of a error throw err.
    if (err) throw err;
  });
}

const characterAI = new CharacterAI();

async function talkToPierre() {
  await characterAI.authenticateAsGuest();

  // Pierre the Peanut
  const pierreId = "lDUsZaTzDTCFq9oj2dovbQwFE5gx0Yb2zYYuXO4UAbY";
  // Discord moderator
  const discordMod = "8_1NyR8w1dOXmI1uWaieQcd147hecbdIK7CeEAIrdJw";
  const chat = await characterAI.createOrContinueChat(pierreId);

  const prompt = getPrompt();

  const response = await chat.sendAndAwaitResponse(prompt.prompt, true);

  console.log("Full Response:\n");
  console.log(response);

  console.log("Selected Response:\n");
  console.log(chooseRandomSentences(removeActions(response.text), prompt.n));

  //writeToOutputFile(removeActions(response.text));
}

(async () => {
  talkToPierre();
})();
