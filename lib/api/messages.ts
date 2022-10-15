import clientPromise from "../mongodb";

export async function checkFormId(form_id: string): Promise<boolean | null> {
  if (!form_id) {
    return false;
  }

  const client = await clientPromise;
  const collection = client.db("roger-bot-db").collection("users");
  const results = await collection.findOne({ form_id });
  if (results) {
    return results;
  } else {
    return null;
  }
}
