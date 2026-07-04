import { DomainError } from "../../../../../Domain Errors/domainErrors.js";
import { connection } from "../../../../../Database Module/Database Connection/databaseConnect.js";
import { createComment,getCommentById,getCommentsByContentId,deleteComment } from "../content coments Repo/contentCommentsRepository.js";
import { ContentRepository } from "../../../content creation models/repository/content.repository.js";

// Create comment
async function createCommentService({ content_id, user_id, comment }) {
    console.log("The user id trying to create account is ",user_id)
  if (!comment || comment.trim().length === 0) {
    throw DomainError.invalid('EMPTY_COMMENT');
  }

  const content = await ContentRepository.findById(content_id);
  if (!content) {
    throw DomainError.notFound('CONTENT_NOT_FOUND');
  }

//   const user = await userRepo.getById(user_id);
  const [user] = await connection.execute('SELECT id FROM users WHERE id = ?', [user_id]);
  if (!user.length) {
    throw DomainError.notFound('USER_NOT_FOUND');
  }
  //check if article is published or not
  const [res] = await connection.execute('SELECT status FROM content WHERE content_id = ?', [content_id]);
  if(res[0].status !== 'published'){
    throw DomainError.invalid('CONTENT_NOT_PUBLISHED');
  }
  
  return createComment({ content_id, user_id, comment });
}

// Get comments
async function getCommentsForContentService(content_id) {
  return getCommentsByContentId(content_id);
}

// Delete comment
async function deleteCommentService({ comment_id, requester_id}) {
  const existing = await getCommentById(comment_id);

  if (!existing) {
    throw DomainError.notFound('COMMENT_NOT_FOUND');
  }

  if (existing.user_id !== requester_id) {
    throw DomainError.invalid('UNAUTHORIZED');
  }

  await deleteComment(comment_id);
}

export{
  createCommentService,
  getCommentsForContentService,
  deleteCommentService,
};
