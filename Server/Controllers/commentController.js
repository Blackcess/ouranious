import { CommentModel } from "../Models/commentModel.js";

const CommentController = {
    // create comment
    async create(req, res) {
        if(!req.user){
            res.status(401).json({msg:"not unathorized to post comment"})
        }
        try {
            const { content_id, comment } = req.body;
            const user_id = req.user.user_id; // assuming Passport.js adds user
            const newComment = await CommentModel.create(content_id, user_id, comment);
            res.status(201).json(newComment);
        } catch (err) {
            res.status(500).json({ error: 'Failed to add comment' });
        }
    },
    // get comments for a content
    async getByContent(req, res) {
        try {
        const comments = await CommentModel.findByContent(req.params.content_id);
        res.json(comments);
        } catch (err) {
            res.status(500).json({ error: 'Failed to fetch comments' });
        }
    },
    // update comment for a content
    async update(req, res) {
        try {
            const { comment } = req.body;
            const updated = await CommentModel.update(req.params.id, comment);
            res.json(updated);
        } catch (err) {
            res.status(500).json({ error: 'Failed to update comment' });
        }
    },
    // delete comment--> reserved for admin and the user who created it only
    async delete(req, res) {
        try {
            await CommentModel.remove(req.params.id);
            res.json({ message: 'Comment deleted' });
        } catch (err) {
            res.status(500).json({ error: 'Failed to delete comment' });
        }
    }
};

export {CommentController}