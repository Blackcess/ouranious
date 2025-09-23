import { connection } from "../Database Module/Database Connection/databaseConnect.js";

const PostAllController = {
    async post(req, res) {
        const { title, slug, body, authorId, category,tags, status ,media} = req.body;

        try {
            // insert article
            const [result] = await connection.query(
                "INSERT INTO content (title, slug, body, author_id, status, published_at) VALUES (?, ?, ?, ?, ?, NOW())",
                [title, slug, body, authorId, status]
            )  ;

            const articleId = result.insertId;

            // handle category if provided
            if (category) {
                // if category is provided, split it into an array
                const sategories = category.split(",").map(cat => cat.trim());
                for (const cat of sategories) {
                    // insert category if it doesn't exist
                    const [rows] = await connection.query(
                        "INSERT IGNORE INTO content_categories (name) VALUES (?)",
                            [cat]
                    );
                    // get the category ID
                     const [catRow] = await connection.query(
                            "SELECT category_id FROM content_categories WHERE name = ?",
                            [cat]
                    );
                     const categoryId = catRow[0].category_id;
                    // link article with category
                    await connection.query(
                    "INSERT INTO content_categories_management (content_id, category_id) VALUES (?, ?)",
                    [articleId, categoryId]
                    );
                } 
            }
            if (tags) {
                // if tags is provided, split it into an array
                const tagsArray = tags.split(",").map(tag => tag.trim());
                for (const tag of tagsArray) {
                    // insert tag if it doesn't exist
                    const [rows] = await connection.query(
                        "INSERT IGNORE INTO tags (name) VALUES (?)",
                            [tag]
                    );
                    // get the tag ID
                        const [tagRow] = await connection.query(
                            "SELECT tag_id FROM tags WHERE name = ?",
                            [tag]
                    );
                        const tagId = tagRow[0].tag_id;
                    // link article with tag
                    await connection.query(
                    "INSERT INTO content_tags (content_id, tag_id) VALUES (?, ?)",
                    [articleId, tagId]
                    );
                }
            }
            // handle media if provided
            if (req.body.media && Array.isArray(req.body.media)) {
                for (const mediaItem of req.body.media) {
                    const { type, attribute, caption, url } = mediaItem;
                    await connection.query(
                        "INSERT INTO media (content_id, file_path, type, attribute) VALUES (?, ?, ?, ?)",
                        [articleId, url, type, caption]
                    );
                }
            }






             await connection.query(`INSERT INTO media (content_id, file_path,type, attribute)
                     VALUES (?, ?,"image", 'coverImage')`, [articleId, req.body.coverImage]);
            

            // respond with success
            res.status(201).json({status:true, message: "Article created", articleId });
        } catch (error) {
            console.error(error);
            res.status(500).json({ message: "Error creating article" });
        }
    }
}

export {PostAllController}