import type { NextApiRequest, NextApiResponse } from "next";

import { checkFormId } from "../../lib/api/messages";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "GET") {
    try {
      const result = await checkFormId(req.query.form_id as string);

      if (result) {
        res.status(200).json({ name: result });
      }
      res.status(403).json({});
    } catch (e: any) {
      console.log(e);
      res.status(500).json({
        error: e.toString(),
      });
    }
  } else if (req.method === "POST") {
    // const { username, bio } = req.body;
    // const session = await getSession({ req });
    // if (!session || session.username !== username) {
    //   return res.status(401).json({
    //     error: "Unauthorized",
    //   });
    // }
    // try {
    //   const result = await updateUser(username, bio);
    //   if (result) {
    //     await res.unstable_revalidate(`/${username}`);
    //   }
    //   const bioMdx = await getMdxSource(bio); // return bioMdx to optimistically show updated state
    //   return res.status(200).json(bioMdx);
    // } catch (e: any) {
    //   console.log(e);
    //   return res.status(500).json({
    //     error: e.toString(),
    //   });
    // }
  } else {
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
