import clientPromise from "../mongodb";

export const sendMessageToAdmins = async (message: string): Promise<void> => {
  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const results = await collection.find({ "is_admin": true, "is_active": true }, {
    '_id': 0, 'telegram_id': 1
  });

  for await (const user of results) {
    await fetch(`https://api.telegram.org/bot${process.env.ROGER_TOKEN_BOT}/sendMessage?chat_id=${user.telegram_id}&text=${message}`, { method: 'POST' })
  }
};
