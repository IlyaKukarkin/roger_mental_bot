import clientPromise from "../mongodb";

export async function checkFormId(form_id: string): Promise<string> {
  if (!form_id) {
    return "";
  }

  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const results = await collection.findOne({ form_id });
  if (results) {
    return results.name;
  } else {
    return "";
  }
}
