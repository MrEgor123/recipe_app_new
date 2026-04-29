import { Tooltip } from "react-tooltip";
import {
  Container,
  Main,
  Button,
  TagsContainer,
  Icons,
  LinkComponent,
} from "../../components";
import { UserContext, AuthContext } from "../../contexts";
import { useContext, useState, useEffect } from "react";
import styles from "./styles.module.css";
import Ingredients from "./ingredients";
import Description from "./description";
import cn from "classnames";
import { useRouteMatch, useParams, useHistory, Link } from "react-router-dom";
import MetaTags from "react-meta-tags";
import DefaultImage from "../../images/userpic-icon.jpg";
import { useRecipe } from "../../utils/index.js";
import api from "../../api";
import { Notification } from "../../components/notification";

const formatCommentDate = (value) => {
  if (!value) return "";
  try {
    return new Date(value).toLocaleString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return value;
  }
};

const getCommentDisplayName = (author = {}) => {
  const fullName = `${author.first_name || ""} ${author.last_name || ""}`.trim();
  return fullName || author.username || "Пользователь";
};

const EditIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
    <path
      d="M4 20h4l10.5-10.5a1.414 1.414 0 0 0 0-2L16.5 5.5a1.414 1.414 0 0 0-2 0L4 16v4z"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const TrashIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
    <path
      d="M5 7h14M9 7V5h6v2m-7 0 1 12h6l1-12"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const CheckSmallIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
    <path
      d="M5 12.5l4.2 4.2L19 7"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const CloseSmallIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
    <path
      d="M7 7l10 10M17 7L7 17"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const HeartIcon = ({ filled = false }) => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
    <path
      d="M12 20.5s-7-4.35-9.2-8.35C1 8.95 2.7 5.5 6.4 5.5c2.05 0 3.28 1.08 4.1 2.2.82-1.12 2.05-2.2 4.1-2.2 3.7 0 5.4 3.45 3.6 6.65C19 16.15 12 20.5 12 20.5z"
      fill={filled ? "currentColor" : "none"}
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const ReplyIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
    <path
      d="M10 8L5 12l5 4M6 12h8c3.314 0 6 2.686 6 6"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const SingleCard = ({ updateOrders }) => {
  const [loading, setLoading] = useState(true);
  const [servings, setServings] = useState(1);

  const [notification, setNotification] = useState({
    text: "",
    position: "-100%",
  });
  const [notificationError, setNotificationError] = useState({
    text: "",
    position: "-100%",
  });

  const [comments, setComments] = useState([]);
  const [commentsLoading, setCommentsLoading] = useState(true);
  const [commentText, setCommentText] = useState("");
  const [commentSubmitting, setCommentSubmitting] = useState(false);

  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editingCommentText, setEditingCommentText] = useState("");
  const [commentActionLoading, setCommentActionLoading] = useState(false);

  const [replyingToId, setReplyingToId] = useState(null);
  const [replyText, setReplyText] = useState("");
  const [replySubmitting, setReplySubmitting] = useState(false);
  const [ratingSubmitting, setRatingSubmitting] = useState(false);

  const [collectionsOpen, setCollectionsOpen] = useState(false);
  const [collectionsLoading, setCollectionsLoading] = useState(false);
  const [collectionsSaving, setCollectionsSaving] = useState(false);
  const [collections, setCollections] = useState([]);
  const [selectedCollectionIds, setSelectedCollectionIds] = useState([]);
  const [newCollectionName, setNewCollectionName] = useState("");
  const [newCollectionSubmitting, setNewCollectionSubmitting] = useState(false);

  const { recipe, setRecipe, handleLike, handleAddToCart, handleSubscribe } =
    useRecipe();

  const authContext = useContext(AuthContext);
  const userContext = useContext(UserContext);
  const { id } = useParams();
  const history = useHistory();
  const { url } = useRouteMatch();

  const showNotification = (text) => {
    setNotification({
      text,
      position: "40px",
    });

    setTimeout(() => {
      setNotification((prev) => ({
        ...prev,
        position: "-100%",
      }));
    }, 3000);
  };

  const sortReplies = (items = []) => {
    return [...items].sort((a, b) => {
      const likesDiff = (b.likes_count || 0) - (a.likes_count || 0);
      if (likesDiff !== 0) return likesDiff;
      return new Date(b.created_at) - new Date(a.created_at);
    });
  };

  const sortComments = (items = []) => {
    return [...items]
      .map((item) => ({
        ...item,
        replies: sortReplies(item.replies || []),
      }))
      .sort((a, b) => {
        const likesDiff = (b.likes_count || 0) - (a.likes_count || 0);
        if (likesDiff !== 0) return likesDiff;
        return new Date(b.created_at) - new Date(a.created_at);
      });
  };

  const loadComments = () => {
    setCommentsLoading(true);
    api
      .getRecipeComments({ recipe_id: id })
      .then((res) => {
        setComments(sortComments(Array.isArray(res) ? res : []));
      })
      .catch((err) => {
        console.log(err);
        setComments([]);
      })
      .finally(() => setCommentsLoading(false));
  };

  const loadRecipe = ({ selectedServings } = {}) => {
    return Promise.all([
      api.getRecipe({ recipe_id: id }),
      api.getRecipeCalculated({
        recipe_id: id,
        servings: selectedServings,
      }),
    ])
      .then(([baseRecipe, calcRecipe]) => {
        const mergedRecipe = {
          ...baseRecipe,
          name: baseRecipe.name || calcRecipe.name || calcRecipe.title || "",
          text: baseRecipe.text || calcRecipe.text || calcRecipe.description || "",
          image: baseRecipe.image || calcRecipe.image || "",
          author: baseRecipe.author || calcRecipe.author || {},
          cooking_time:
            baseRecipe.cooking_time ||
            calcRecipe.cooking_time ||
            calcRecipe.cooking_time_minutes ||
            0,
          ingredients: (calcRecipe.ingredients || []).map((item) => ({
            ...item,
            measurement_unit: item.measurement_unit || item.unit,
          })),
          base_servings: calcRecipe.base_servings || 1,
          selected_servings:
            calcRecipe.selected_servings ||
            selectedServings ||
            calcRecipe.base_servings ||
            1,
          nutrition_total: calcRecipe.nutrition_total || {},
          nutrition_per_serving: calcRecipe.nutrition_per_serving || {},
        };

        setRecipe(mergedRecipe);
        setServings(mergedRecipe.selected_servings || 1);
        setLoading(false);
      })
      .catch((err) => {
        console.log(err);
        history.push("/not-found");
      });
  };

  const loadCollectionsModalData = () => {
    if (!authContext) return;

    setCollectionsLoading(true);

    Promise.all([api.getCollections(), api.getRecipeCollections({ recipe_id: id })])
      .then(([collectionsData, recipeCollectionsData]) => {
        setCollections(Array.isArray(collectionsData) ? collectionsData : []);
        setSelectedCollectionIds(
          Array.isArray(recipeCollectionsData.collection_ids)
            ? recipeCollectionsData.collection_ids
            : []
        );
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось загрузить подборки",
          position: "40px",
        });
      })
      .finally(() => setCollectionsLoading(false));
  };

  const openCollectionsModal = () => {
    setCollectionsOpen(true);
    setNewCollectionName("");
    loadCollectionsModalData();
  };

  const closeCollectionsModal = () => {
    if (collectionsSaving || newCollectionSubmitting) return;
    setCollectionsOpen(false);
    setNewCollectionName("");
  };

  const toggleCollectionSelection = (collectionId) => {
    setSelectedCollectionIds((prev) =>
      prev.includes(collectionId)
        ? prev.filter((itemId) => itemId !== collectionId)
        : [...prev, collectionId]
    );
  };

  const handleSaveCollections = () => {
    if (!authContext || collectionsSaving) return;

    setCollectionsSaving(true);

    api
      .updateRecipeCollections({
        recipe_id: id,
        collection_ids: selectedCollectionIds,
      })
      .then((res) => {
        setSelectedCollectionIds(res.collection_ids || []);
        setCollectionsOpen(false);
        showNotification("Подборки сохранены");
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: err?.detail || "Не удалось сохранить подборки",
          position: "40px",
        });
      })
      .finally(() => setCollectionsSaving(false));
  };

  const handleCreateCollection = () => {
    const name = newCollectionName.trim();
    if (!name || newCollectionSubmitting) return;

    setNewCollectionSubmitting(true);

    api
      .createCollection({ name })
      .then((createdCollection) => {
        setCollections((prev) => [createdCollection, ...prev]);
        setSelectedCollectionIds((prev) =>
          prev.includes(createdCollection.id)
            ? prev
            : [...prev, createdCollection.id]
        );
        setNewCollectionName("");
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: err?.detail || "Не удалось создать подборку",
          position: "40px",
        });
      })
      .finally(() => setNewCollectionSubmitting(false));
  };

  const replaceCommentInTree = (items, commentId, updater) =>
    items.map((item) => {
      if (item.id === commentId) {
        return updater(item);
      }
      if (item.replies && item.replies.length) {
        return {
          ...item,
          replies: replaceCommentInTree(item.replies, commentId, updater),
        };
      }
      return item;
    });

  const removeCommentFromTree = (items, commentId) =>
    items
      .filter((item) => item.id !== commentId)
      .map((item) => ({
        ...item,
        replies: item.replies ? removeCommentFromTree(item.replies, commentId) : [],
      }));

  const addReplyToTree = (items, parentId, reply) =>
    items.map((item) => {
      if (item.id === parentId) {
        return {
          ...item,
          replies: sortReplies([reply, ...(item.replies || [])]),
        };
      }
      if (item.replies && item.replies.length) {
        return {
          ...item,
          replies: addReplyToTree(item.replies, parentId, reply),
        };
      }
      return item;
    });

  const handleCopyLink = () => {
    api
      .copyRecipeLink({ id })
      .then(({ "short-link": shortLink }) => {
        navigator.clipboard
          .writeText(shortLink)
          .then(() => {
            showNotification("Ссылка скопирована");
          })
          .catch(() => {
            setNotificationError({
              text: `Ваша ссылка: ${shortLink}`,
              position: "40px",
            });
          });
      })
      .catch((err) => console.log(err));
  };

  const handleErrorClose = () => {
    setNotificationError((prev) => ({ ...prev, position: "-100%" }));
  };

  const handleRateRecipe = (rating) => {
    if (!authContext || ratingSubmitting) return;

    setRatingSubmitting(true);

    api
      .rateRecipe({ recipe_id: id, rating })
      .then((ratingData) => {
        setRecipe((prev) => ({
          ...prev,
          rating_avg: ratingData.rating_avg,
          rating_count: ratingData.rating_count,
          user_rating: ratingData.user_rating,
        }));
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось поставить оценку",
          position: "40px",
        });
      })
      .finally(() => setRatingSubmitting(false));
  };

  const handleDeleteRating = () => {
    if (!authContext || ratingSubmitting) return;

    setRatingSubmitting(true);

    api
      .deleteRecipeRating({ recipe_id: id })
      .then(() => loadRecipe({ selectedServings: servings }))
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось удалить оценку",
          position: "40px",
        });
      })
      .finally(() => setRatingSubmitting(false));
  };

  const handleCommentSubmit = (e) => {
    e.preventDefault();

    const text = commentText.trim();
    if (!text || commentSubmitting) return;

    setCommentSubmitting(true);

    api
      .createRecipeComment({
        recipe_id: id,
        text,
        parent_id: null,
      })
      .then((newComment) => {
        setComments((prev) => sortComments([newComment, ...prev]));
        setCommentText("");
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось отправить комментарий",
          position: "40px",
        });
      })
      .finally(() => setCommentSubmitting(false));
  };

  const handleReplySubmit = (parentId) => {
    const text = replyText.trim();
    if (!text || replySubmitting) return;

    setReplySubmitting(true);

    api
      .createRecipeComment({
        recipe_id: id,
        text,
        parent_id: parentId,
      })
      .then((newReply) => {
        setComments((prev) => addReplyToTree(prev, parentId, newReply));
        setReplyText("");
        setReplyingToId(null);
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось отправить ответ",
          position: "40px",
        });
      })
      .finally(() => setReplySubmitting(false));
  };

  const handleStartEditComment = (comment) => {
    setEditingCommentId(comment.id);
    setEditingCommentText(comment.text);
  };

  const handleCancelEditComment = () => {
    setEditingCommentId(null);
    setEditingCommentText("");
  };

  const handleSaveEditComment = (commentId) => {
    const text = editingCommentText.trim();
    if (!text || commentActionLoading) return;

    setCommentActionLoading(true);

    api
      .patchComment({
        comment_id: commentId,
        text,
      })
      .then((updatedComment) => {
        setComments((prev) =>
          sortComments(
            replaceCommentInTree(prev, commentId, (item) => ({
              ...updatedComment,
              replies: item.replies || [],
            }))
          )
        );
        setEditingCommentId(null);
        setEditingCommentText("");
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось обновить комментарий",
          position: "40px",
        });
      })
      .finally(() => setCommentActionLoading(false));
  };

  const handleDeleteComment = (commentId) => {
    if (commentActionLoading) return;
    if (!window.confirm("Удалить комментарий?")) return;

    setCommentActionLoading(true);

    api
      .deleteComment({ comment_id: commentId })
      .then(() => {
        setComments((prev) => removeCommentFromTree(prev, commentId));
        if (editingCommentId === commentId) {
          setEditingCommentId(null);
          setEditingCommentText("");
        }
        if (replyingToId === commentId) {
          setReplyingToId(null);
          setReplyText("");
        }
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось удалить комментарий",
          position: "40px",
        });
      })
      .finally(() => setCommentActionLoading(false));
  };

  const handleToggleCommentLike = (comment) => {
    if (!authContext || commentActionLoading) return;

    setCommentActionLoading(true);

    const request = comment.is_liked
      ? api.unlikeComment({ comment_id: comment.id })
      : api.likeComment({ comment_id: comment.id });

    request
      .then((updatedComment) => {
        setComments((prev) =>
          sortComments(
            replaceCommentInTree(prev, comment.id, (item) => ({
              ...updatedComment,
              replies: item.replies || [],
            }))
          )
        );
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось обновить лайк",
          position: "40px",
        });
      })
      .finally(() => setCommentActionLoading(false));
  };

  const handleDecreaseServings = () => {
    if (servings <= 1) return;
    loadRecipe({ selectedServings: servings - 1 });
  };

  const handleIncreaseServings = () => {
    loadRecipe({ selectedServings: servings + 1 });
  };

  useEffect(() => {
    setLoading(true);
    loadRecipe();
    loadComments();
  }, [id]);

  const {
    author = {},
    image,
    tags,
    cooking_time,
    name,
    ingredients = [],
    text,
    is_favorited,
    is_in_shopping_cart,
    rating_avg = 0,
    rating_count = 0,
    user_rating = null,
    base_servings = 1,
    selected_servings = 1,
    nutrition_total = {},
    nutrition_per_serving = {},
  } = recipe;

  const renderComment = (comment, isReply = false) => {
    const isOwner =
      authContext &&
      userContext &&
      comment.author &&
      Number(comment.author.id) === Number(userContext.id);

    const isEditing = editingCommentId === comment.id;
    const isReplying = replyingToId === comment.id;
    const authorId = (comment.author || {}).id;
    const authorName = getCommentDisplayName(comment.author);

    return (
      <div
        className={cn(styles.commentCard, {
          [styles.replyCard]: isReply,
        })}
        key={comment.id}
      >
        <div className={styles.commentTop}>
          <Link
            to={`/users/${authorId}`}
            className={styles.commentAvatarLink}
            aria-label={`Открыть профиль ${authorName}`}
          >
            <div
              className={styles.commentAvatar}
              style={{
                backgroundImage: `url(${(comment.author || {}).avatar || DefaultImage})`,
              }}
            />
          </Link>

          <div className={styles.commentMeta}>
            <Link to={`/users/${authorId}`} className={styles.commentAuthorLink}>
              {authorName}
            </Link>
            <div className={styles.commentDate}>
              {formatCommentDate(comment.created_at)}
            </div>
          </div>

          <div className={styles.commentRightActions}>
            <button
              type="button"
              className={cn(styles.commentLikeBtn, {
                [styles.commentLikeBtnActive]: comment.is_liked,
              })}
              onClick={() => handleToggleCommentLike(comment)}
              disabled={!authContext}
              title={
                authContext
                  ? comment.is_liked
                    ? "Убрать лайк"
                    : "Поставить лайк"
                  : "Войдите, чтобы поставить лайк"
              }
              aria-label="Лайк комментария"
            >
              <HeartIcon filled={comment.is_liked} />
              <span className={styles.commentLikeCount}>
                {comment.likes_count || 0}
              </span>
            </button>

            {authContext && !isReply && (
              <button
                type="button"
                className={styles.commentReplyBtn}
                onClick={() => {
                  setReplyingToId(comment.id);
                  setReplyText("");
                }}
                title="Ответить"
                aria-label="Ответить на комментарий"
              >
                <ReplyIcon />
              </button>
            )}

            {isOwner && (
              <div className={styles.commentActions}>
                {!isEditing ? (
                  <>
                    <button
                      type="button"
                      className={styles.commentActionIconBtn}
                      onClick={() => handleStartEditComment(comment)}
                      title="Редактировать"
                      aria-label="Редактировать комментарий"
                    >
                      <EditIcon />
                    </button>
                    <button
                      type="button"
                      className={cn(
                        styles.commentActionIconBtn,
                        styles.commentDeleteIconBtn
                      )}
                      onClick={() => handleDeleteComment(comment.id)}
                      title="Удалить"
                      aria-label="Удалить комментарий"
                    >
                      <TrashIcon />
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      className={cn(
                        styles.commentActionIconBtn,
                        styles.commentSaveIconBtn
                      )}
                      onClick={() => handleSaveEditComment(comment.id)}
                      title="Сохранить"
                      aria-label="Сохранить комментарий"
                    >
                      <CheckSmallIcon />
                    </button>
                    <button
                      type="button"
                      className={styles.commentActionIconBtn}
                      onClick={handleCancelEditComment}
                      title="Отмена"
                      aria-label="Отменить редактирование"
                    >
                      <CloseSmallIcon />
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        </div>

        {isEditing ? (
          <textarea
            className={styles.commentEditTextarea}
            value={editingCommentText}
            onChange={(e) => setEditingCommentText(e.target.value)}
            maxLength={2000}
          />
        ) : (
          <div className={styles.commentText}>{comment.text}</div>
        )}

        {isReplying && (
          <div className={styles.replyForm}>
            <textarea
              className={styles.replyTextarea}
              placeholder={`Ответ для ${authorName}`}
              value={replyText}
              onChange={(e) => setReplyText(e.target.value)}
              maxLength={2000}
            />
            <div className={styles.replyFormFooter}>
              <button
                type="button"
                className={styles.replyCancelBtn}
                onClick={() => {
                  setReplyingToId(null);
                  setReplyText("");
                }}
              >
                Отмена
              </button>
              <Button
                className={styles.replySubmitBtn}
                modifier="style_dark"
                type="button"
                disabled={!replyText.trim() || replySubmitting}
                clickHandler={() => handleReplySubmit(comment.id)}
              >
                {replySubmitting ? "Отправка..." : "Ответить"}
              </Button>
            </div>
          </div>
        )}

        {!!comment.replies?.length && (
          <div className={styles.repliesList}>
            {comment.replies.map((reply) => renderComment(reply, true))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <Main>
        <Container>
          <div className={styles.page}>Загрузка...</div>
        </Container>
      </Main>
    );
  }

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>{name}</title>
          <meta name="description" content={`Recepto - ${name}`} />
          <meta property="og:title" content={name} />
        </MetaTags>

        <div className={styles.page}>
          <div className={styles.heroGrid}>
            <div className={styles.media}>
              <img src={image} alt={name} className={styles.image} />
            </div>

            <div className={styles.content}>
              <div className={styles.header}>
                <h1 className={styles.title}>{name}</h1>

                <div className={styles.actions}>
                  <Button
                    modifier="style_none"
                    clickHandler={handleCopyLink}
                    className={styles.iconBtn}
                    data-tooltip-id="tooltip-copy"
                    data-tooltip-content="Скопировать ссылку"
                    data-tooltip-place="top"
                  >
                    <Icons.CopyLinkIcon />
                  </Button>
                  <Tooltip id="tooltip-copy" />

                  {authContext && (
                    <>
                      <Button
                        modifier="style_none"
                        clickHandler={() => {
                          handleLike({ id, toLike: Number(!is_favorited) });
                        }}
                        className={cn(styles.iconBtn, {
                          [styles.iconBtnActive]: is_favorited,
                        })}
                        data-tooltip-id="tooltip-save"
                        data-tooltip-content={
                          is_favorited
                            ? "Удалить из избранного"
                            : "Добавить в избранное"
                        }
                        data-tooltip-place="bottom"
                      >
                        <Icons.LikeIcon />
                      </Button>
                      <Tooltip id="tooltip-save" />
                    </>
                  )}
                </div>
              </div>

              <div className={styles.metaRow}>
                <TagsContainer tags={tags} />
                <span className={styles.metaItem}>{cooking_time} мин.</span>
                <span className={styles.divider} />
                <div className={styles.metaItem}>
                  <div
                    className={styles.authorAvatar}
                    style={{
                      backgroundImage: `url(${author.avatar || DefaultImage})`,
                    }}
                  />
                  <LinkComponent
                    title={`${author.first_name} ${author.last_name}`}
                    href={`/users/${author.id}`}
                    className={styles.authorLink}
                  />
                </div>
              </div>

              <div className={styles.ratingSection}>
                <div className={styles.ratingSummary}>
                  <div className={styles.ratingBadge}>
                    <span className={styles.ratingStar}>★</span>
                    <span className={styles.ratingValue}>
                      {Number(rating_avg || 0).toFixed(1)}
                    </span>
                  </div>
                  <span className={styles.ratingCount}>
                    Оценок: {rating_count || 0}
                  </span>
                </div>

                {authContext ? (
                  <div className={styles.ratingControls}>
                    <div className={styles.ratingButtons}>
                      {[1, 2, 3, 4, 5].map((value) => (
                        <button
                          key={value}
                          type="button"
                          className={cn(styles.ratingBtn, {
                            [styles.ratingBtnActive]: Number(user_rating) === value,
                          })}
                          onClick={() => handleRateRecipe(value)}
                          disabled={ratingSubmitting}
                        >
                          {value}
                        </button>
                      ))}
                    </div>

                    {user_rating ? (
                      <button
                        type="button"
                        className={styles.ratingDeleteBtn}
                        onClick={handleDeleteRating}
                        disabled={ratingSubmitting}
                      >
                        Убрать оценку
                      </button>
                    ) : null}
                  </div>
                ) : (
                  <div className={styles.ratingAuthNote}>
                    Войдите в аккаунт, чтобы поставить оценку
                  </div>
                )}
              </div>

              {(userContext || {}).id !== author.id && authContext && (
                <div className={styles.subscribeRow}>
                  <Button
                    className={cn(styles.subscribeBtn, {
                      [styles.subscribeBtnActive]: author.is_subscribed,
                    })}
                    modifier={author.is_subscribed ? "style_dark" : "style_light"}
                    clickHandler={() => {
                      handleSubscribe({
                        author_id: author.id,
                        toSubscribe: !author.is_subscribed,
                      });
                    }}
                    data-tooltip-id="tooltip-subscribe"
                    data-tooltip-content={
                      author.is_subscribed
                        ? "Отписаться от автора"
                        : "Подписаться на автора"
                    }
                    data-tooltip-place="bottom"
                  >
                    <Icons.AddUser />
                    {author.is_subscribed ? "Вы подписаны" : "Подписаться"}
                  </Button>
                  <Tooltip id="tooltip-subscribe" />
                </div>
              )}

              <div className={styles.primaryRow}>
                {authContext && (
                  <Button
                    className={styles.primaryBtn}
                    modifier="style_dark"
                    clickHandler={() => {
                      handleAddToCart({
                        id,
                        toAdd: Number(!is_in_shopping_cart),
                        callback: updateOrders,
                      });
                    }}
                  >
                    {is_in_shopping_cart ? (
                      <>
                        <Icons.CheckIcon />
                        Рецепт добавлен
                      </>
                    ) : (
                      <>
                        <Icons.PlusIcon />
                        Добавить в покупки
                      </>
                    )}
                  </Button>
                )}

                {authContext && (
                  <Button
                    className={styles.editBtn}
                    modifier="style_light"
                    clickHandler={openCollectionsModal}
                  >
                    В подборки
                  </Button>
                )}

                {authContext && (userContext || {}).id === author.id && (
                  <Button
                    href={`${url}/edit`}
                    className={styles.editBtn}
                    modifier="style_light"
                  >
                    Редактировать рецепт
                  </Button>
                )}
              </div>
            </div>
          </div>

          <div className={styles.detailsGrid}>
            <div className={styles.infoCard}>
              <Ingredients ingredients={ingredients} />
            </div>

            <div className={styles.infoCard}>
              <div className={styles.servingsBlock}>
                <div className={styles.servingsInfo}>
                  <div className={styles.servingsTitle}>Порции</div>
                  <div className={styles.servingsHint}>
                    Базовое количество порций: {base_servings}
                  </div>
                </div>

                <div className={styles.servingsControls}>
                  <button
                    type="button"
                    className={styles.servingsBtn}
                    onClick={handleDecreaseServings}
                    disabled={servings <= 1}
                  >
                    −
                  </button>

                  <div className={styles.servingsValue}>{selected_servings}</div>

                  <button
                    type="button"
                    className={styles.servingsBtn}
                    onClick={handleIncreaseServings}
                  >
                    +
                  </button>
                </div>
              </div>

              <div className={styles.nutritionBlock}>
                <div className={styles.nutritionTitle}>КБЖУ</div>

                <div className={styles.nutritionGrid}>
                  <div className={styles.nutritionItem}>
                    <span className={styles.nutritionLabel}>Калории</span>
                    <span className={styles.nutritionValue}>
                      {Number(nutrition_total.calories || 0).toFixed(2)} ккал
                    </span>
                  </div>

                  <div className={styles.nutritionItem}>
                    <span className={styles.nutritionLabel}>Белки</span>
                    <span className={styles.nutritionValue}>
                      {Number(nutrition_total.protein || 0).toFixed(2)} г
                    </span>
                  </div>

                  <div className={styles.nutritionItem}>
                    <span className={styles.nutritionLabel}>Жиры</span>
                    <span className={styles.nutritionValue}>
                      {Number(nutrition_total.fat || 0).toFixed(2)} г
                    </span>
                  </div>

                  <div className={styles.nutritionItem}>
                    <span className={styles.nutritionLabel}>Углеводы</span>
                    <span className={styles.nutritionValue}>
                      {Number(nutrition_total.carbs || 0).toFixed(2)} г
                    </span>
                  </div>
                </div>

                <div className={styles.nutritionPerServing}>
                  На 1 порцию:{" "}
                  {Number(nutrition_per_serving.calories || 0).toFixed(2)} ккал /{" "}
                  {Number(nutrition_per_serving.protein || 0).toFixed(2)} Б /{" "}
                  {Number(nutrition_per_serving.fat || 0).toFixed(2)} Ж /{" "}
                  {Number(nutrition_per_serving.carbs || 0).toFixed(2)} У
                </div>
              </div>
            </div>
          </div>

          <div className={styles.fullWidthSection}>
            <div className={styles.infoCard}>
              <Description description={text} />
            </div>
          </div>

          <div className={styles.commentsSection}>
            <div className={styles.commentsBlock}>
              <div className={styles.commentsHeader}>
                <h2 className={styles.commentsTitle}>Комментарии</h2>
                <span className={styles.commentsCount}>{comments.length}</span>
              </div>

              {authContext ? (
                <form className={styles.commentForm} onSubmit={handleCommentSubmit}>
                  <textarea
                    className={styles.commentTextarea}
                    placeholder="Напишите комментарий"
                    value={commentText}
                    onChange={(e) => setCommentText(e.target.value)}
                    maxLength={2000}
                  />
                  <div className={styles.commentFormFooter}>
                    <span className={styles.commentHint}>
                      {commentText.trim().length}/2000
                    </span>
                    <Button
                      className={styles.commentSubmitBtn}
                      modifier="style_dark"
                      type="submit"
                      disabled={!commentText.trim() || commentSubmitting}
                    >
                      {commentSubmitting ? "Отправка..." : "Отправить"}
                    </Button>
                  </div>
                </form>
              ) : (
                <div className={styles.commentAuthNote}>
                  Войдите в аккаунт, чтобы оставить комментарий
                </div>
              )}

              <div className={styles.commentsList}>
                {commentsLoading ? (
                  <div className={styles.commentsEmpty}>
                    Загрузка комментариев...
                  </div>
                ) : comments.length ? (
                  comments.map((comment) => renderComment(comment))
                ) : (
                  <div className={styles.commentsEmpty}>
                    Пока нет комментариев. Будьте первым, кто оставит отзыв.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {collectionsOpen && (
          <div className={styles.collectionsModalOverlay} onClick={closeCollectionsModal}>
            <div
              className={styles.collectionsModal}
              onClick={(e) => e.stopPropagation()}
            >
              <div className={styles.collectionsModalHeader}>
                <h3 className={styles.collectionsModalTitle}>Подборки</h3>
                <button
                  type="button"
                  className={styles.collectionsModalClose}
                  onClick={closeCollectionsModal}
                >
                  ×
                </button>
              </div>

              <div className={styles.collectionsModalBody}>
                <div className={styles.collectionsCreateRow}>
                  <input
                    type="text"
                    className={styles.collectionsInput}
                    placeholder="Новая подборка"
                    value={newCollectionName}
                    onChange={(e) => setNewCollectionName(e.target.value)}
                    maxLength={100}
                  />
                  <Button
                    className={styles.collectionsCreateBtn}
                    modifier="style_dark"
                    clickHandler={handleCreateCollection}
                    disabled={!newCollectionName.trim() || newCollectionSubmitting}
                  >
                    {newCollectionSubmitting ? "Создание..." : "Создать"}
                  </Button>
                </div>

                {collectionsLoading ? (
                  <div className={styles.collectionsEmpty}>Загрузка подборок...</div>
                ) : collections.length ? (
                  <div className={styles.collectionsList}>
                    {collections.map((collection) => (
                      <label key={collection.id} className={styles.collectionsItem}>
                        <input
                          type="checkbox"
                          checked={selectedCollectionIds.includes(collection.id)}
                          onChange={() => toggleCollectionSelection(collection.id)}
                        />
                        <span className={styles.collectionsItemName}>
                          {collection.name}
                        </span>
                        <span className={styles.collectionsItemCount}>
                          {collection.recipes_count || 0}
                        </span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <div className={styles.collectionsEmpty}>
                    У вас пока нет подборок
                  </div>
                )}
              </div>

              <div className={styles.collectionsModalFooter}>
                <button
                  type="button"
                  className={styles.collectionsCancelBtn}
                  onClick={closeCollectionsModal}
                >
                  Отмена
                </button>
                <Button
                  className={styles.collectionsSaveBtn}
                  modifier="style_dark"
                  clickHandler={handleSaveCollections}
                  disabled={collectionsSaving}
                >
                  {collectionsSaving ? "Сохранение..." : "Сохранить"}
                </Button>
              </div>
            </div>
          </div>
        )}

        <Notification
          text={notification.text}
          style={{ right: notification.position }}
        />
        <Notification
          text={notificationError.text}
          style={{ right: notificationError.position }}
          onClose={handleErrorClose}
        />
      </Container>
    </Main>
  );
};

export default SingleCard;