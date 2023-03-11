const CharacterAI = require("node_characterai");
const characterAI = new CharacterAI();

async function talkToPierre() {
  await characterAI.authenticateAsGuest();

  // Pierre the Peanut
  const pierreId = "lDUsZaTzDTCFq9oj2dovbQwFE5gx0Yb2zYYuXO4UAbY";
  // Discord moderator
  const discordMod = "8_1NyR8w1dOXmI1uWaieQcd147hecbdIK7CeEAIrdJw";
  const chat = await characterAI.createOrContinueChat(pierreId);
  const response = await chat.sendAndAwaitResponse("What are you up to?", true);

  console.log(response);
  // use response.text to use it in a string.
}

(async () => {
  talkToPierre();
})();
