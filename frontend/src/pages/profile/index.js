import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useHistory, useParams } from "react-router-dom";
import MetaTags from "react-meta-tags";
import cn from "classnames";

import {
  Container,
  Main,
  Button,
  Icons,
  CollectionModal,
} from "../../components";
import { Notification } from "../../components/notification";
import api from "../../api";
import styles from "./styles.module.css";
import DefaultImage from "../../images/userpic-icon.jpg";

const formatJoinDate = (value) => {
  if (!value) return "";
  try {
    return new Date(value).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return value;
  }
};

const formatCollectionDate = (value) => {
  if (!value) return "";
  try {
    return new Date(value).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return value;
  }
};

const formatCommentDate = (value) => {
  if (!value) return "";
  try {
    return new Date(value).toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return value;
  }
};

const ProfilePage = ({ isMe = false }) => {
  const history = useHistory();
  const { id } = useParams();
  const avatarInputRef = useRef(null);

  const [loading, setLoading] = useState(true);
  const [collectionsLoading, setCollectionsLoading] = useState(false);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [collectionSaving, setCollectionSaving] = useState(false);
  const [subscribeLoading, setSubscribeLoading] = useState(false);
  const [avatarUploading, setAvatarUploading] = useState(false);
  const [profile, setProfile] = useState(null);
  const [collections, setCollections] = useState([]);
  const [comments, setComments] = useState([]);
  const [activeTab, setActiveTab] = useState("recipes");
  const [notificationError, setNotificationError] = useState({
    text: "",
    position: "-100%",
  });

  const [isCollectionModalOpen, setIsCollectionModalOpen] = useState(false);
  const [editingCollection, setEditingCollection] = useState(null);

  const profileId = useMemo(() => {
    if (isMe) return null;
    return id;
  }, [id, isMe]);

  useEffect(() => {
    setLoading(true);

    const request = isMe
      ? api.getMyProfile()
      : api.getProfile({ user_id: profileId });

    request
      .then((data) => {
        setProfile(data);
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось загрузить профиль",
          position: "40px",
        });
      })
      .finally(() => setLoading(false));
  }, [isMe, profileId]);

  const loadCollections = () => {
    if (!profile) return;

    setCollectionsLoading(true);

    const request = isMe
      ? api.getMyCollectionsProfile()
      : api.getUserCollections({ user_id: profile.id });

    request
      .then((data) => {
        setCollections(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.log(err);
        setCollections([]);
      })
      .finally(() => setCollectionsLoading(false));
  };

  const loadComments = () => {
    if (!profile) return;

    setCommentsLoading(true);

    const request = isMe
      ? api.getMyProfileComments()
      : api.getUserProfileComments({ user_id: profile.id });

    request
      .then((data) => {
        setComments(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.log(err);
        setComments([]);
      })
      .finally(() => setCommentsLoading(false));
  };

  useEffect(() => {
    loadCollections();
    loadComments();
  }, [profile, isMe]);

  const handleErrorClose = () => {
    setNotificationError((prev) => ({ ...prev, position: "-100%" }));
  };

  const openAvatarPicker = () => {
    if (!profile?.is_owner || avatarUploading) return;
    avatarInputRef.current?.click();
  };

  const handleAvatarChange = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      setNotificationError({
        text: "Нужно выбрать изображение",
        position: "40px",
      });
      event.target.value = "";
      return;
    }

    const reader = new FileReader();

    reader.onloadend = () => {
      const result = reader.result;

      if (typeof result !== "string") {
        setNotificationError({
          text: "Не удалось обработать изображение",
          position: "40px",
        });
        event.target.value = "";
        return;
      }

      setAvatarUploading(true);

      api
        .changeAvatar({ file: result })
        .then((res) => {
          setProfile((prev) =>
            prev
              ? {
                  ...prev,
                  avatar: res.avatar || prev.avatar,
                }
              : prev
          );
          event.target.value = "";
        })
        .catch((err) => {
          console.log(err);
          setNotificationError({
            text: "Не удалось обновить аватар",
            position: "40px",
          });
          event.target.value = "";
        })
        .finally(() => setAvatarUploading(false));
    };

    reader.readAsDataURL(file);
  };

  const openCreateCollectionModal = () => {
    setEditingCollection(null);
    setIsCollectionModalOpen(true);
  };

  const openEditCollectionModal = (collection) => {
    setEditingCollection(collection);
    setIsCollectionModalOpen(true);
  };

  const closeCollectionModal = () => {
    if (collectionSaving) return;
    setIsCollectionModalOpen(false);
    setEditingCollection(null);
  };

  const handleSubmitCollection = ({ name, description }) => {
    setCollectionSaving(true);

    const request = editingCollection
      ? api.updateCollection({
          collection_id: editingCollection.id,
          name,
          description,
        })
      : api.createCollection({ name, description });

    request
      .then((savedCollection) => {
        if (editingCollection) {
          setCollections((prev) =>
            prev.map((item) =>
              item.id === savedCollection.id ? savedCollection : item
            )
          );
        } else {
          setCollections((prev) => [savedCollection, ...prev]);
        }

        setIsCollectionModalOpen(false);
        setEditingCollection(null);
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось сохранить подборку",
          position: "40px",
        });
      })
      .finally(() => setCollectionSaving(false));
  };

  const handleDeleteCollection = (collectionId) => {
    if (!window.confirm("Удалить подборку?")) return;

    api
      .deleteCollection({ collection_id: collectionId })
      .then(() => {
        setCollections((prev) =>
          prev.filter((item) => item.id !== collectionId)
        );
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось удалить подборку",
          position: "40px",
        });
      });
  };

  const handleToggleSubscribe = () => {
    if (!profile || profile.is_owner || subscribeLoading) return;

    const wasSubscribed = profile.is_subscribed;

    setSubscribeLoading(true);

    const request = wasSubscribed
      ? api.deleteSubscriptions({ author_id: profile.id })
      : api.subscribe({ author_id: profile.id });

    request
      .then(() => {
        const reloadRequest = isMe
          ? api.getMyProfile()
          : api.getProfile({ user_id: profile.id });

        return reloadRequest;
      })
      .then((updatedProfile) => {
        setProfile(updatedProfile);
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: wasSubscribed
            ? "Не удалось отменить подписку"
            : "Не удалось подписаться",
          position: "40px",
        });
      })
      .finally(() => setSubscribeLoading(false));
  };

  if (loading) {
    return (
      <Main>
        <Container>
          <div className={styles.page}>
            <div className={styles.emptyCard}>
              <h1 className={styles.emptyTitle}>Загрузка профиля...</h1>
            </div>
          </div>
        </Container>
      </Main>
    );
  }

  if (!profile) {
    return (
      <Main>
        <Container>
          <div className={styles.page}>
            <div className={styles.emptyCard}>
              <h1 className={styles.emptyTitle}>Профиль не найден</h1>
              <p className={styles.emptyText}>
                Не удалось загрузить данные пользователя
              </p>
              <Button
                className={styles.backBtn}
                modifier="style_dark"
                clickHandler={() => history.push("/")}
              >
                На главную
              </Button>
            </div>
          </div>
        </Container>
      </Main>
    );
  }

  const fullName =
    `${profile.first_name || ""} ${profile.last_name || ""}`.trim() ||
    profile.username;

  const {
    avatar,
    cover_image,
    username,
    status,
    bio,
    created_at,
    is_owner,
    is_subscribed,
    stats = {},
    recipes = [],
  } = profile;

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>{is_owner ? "Мой профиль" : fullName}</title>
          <meta name="description" content={`Recepto - профиль ${fullName}`} />
          <meta property="og:title" content={fullName} />
        </MetaTags>

        <div className={styles.page}>
          <div
            className={styles.cover}
            style={
              cover_image ? { backgroundImage: `url(${cover_image})` } : undefined
            }
          >
            {!cover_image && <div className={styles.coverPlaceholder} />}
          </div>

          <div className={styles.profileCard}>
            <div className={styles.profileTop}>
              <div className={styles.avatarWrap}>
                <button
                  type="button"
                  className={cn(styles.avatarButton, {
                    [styles.avatarButtonEditable]: is_owner,
                    [styles.avatarButtonLoading]: avatarUploading,
                  })}
                  onClick={openAvatarPicker}
                  disabled={!is_owner || avatarUploading}
                  title={is_owner ? "Нажмите, чтобы изменить аватар" : undefined}
                >
                  <div
                    className={styles.avatar}
                    style={{
                      backgroundImage: `url(${avatar || DefaultImage})`,
                    }}
                  />
                  {is_owner && (
                    <span className={styles.avatarHint}>
                      {avatarUploading ? "Загрузка..." : "Изменить"}
                    </span>
                  )}
                </button>

                {is_owner && (
                  <input
                    ref={avatarInputRef}
                    type="file"
                    accept="image/*"
                    className={styles.hiddenInput}
                    onChange={handleAvatarChange}
                  />
                )}
              </div>

              <div className={styles.profileMain}>
                <div className={styles.profileHeader}>
                  <div className={styles.profileTitleWrap}>
                    <h1 className={styles.profileTitle}>{fullName}</h1>
                    <div className={styles.profileUsername}>@{username}</div>
                  </div>

                  <div className={styles.profileActions}>
                    {is_owner ? (
                      <Button
                        className={styles.profileActionBtn}
                        modifier="style_light"
                        type="button"
                        clickHandler={() => history.push("/profile/edit")}
                      >
                        Редактировать профиль
                      </Button>
                    ) : (
                      <Button
                        className={cn(styles.profileActionBtn, {
                          [styles.profileActionBtnActive]: is_subscribed,
                        })}
                        modifier={is_subscribed ? "style_dark" : "style_light"}
                        type="button"
                        clickHandler={handleToggleSubscribe}
                        disabled={subscribeLoading}
                      >
                        {subscribeLoading
                          ? is_subscribed
                            ? "Отписка..."
                            : "Подписка..."
                          : is_subscribed
                            ? "Вы подписаны"
                            : "Подписаться"}
                      </Button>
                    )}
                  </div>
                </div>

                <div className={styles.profileMeta}>
                  <span className={styles.profileStatus}>
                    {status || "Статус пока не указан"}
                  </span>
                  <span className={styles.profileDot} />
                  <span className={styles.profileDate}>
                    С нами с {formatJoinDate(created_at)}
                  </span>
                </div>

                <div
                  className={cn(styles.profileBio, {
                    [styles.profileBioMuted]: !bio,
                  })}
                >
                  {bio || "Пользователь пока не добавил описание профиля"}
                </div>
              </div>
            </div>

            <div className={styles.statsGrid}>
              <div className={styles.statCard}>
                <span className={styles.statValue}>{stats.recipes_count || 0}</span>
                <span className={styles.statLabel}>Рецепты</span>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statValue}>
                  {stats.followers_count || 0}
                </span>
                <span className={styles.statLabel}>Подписчики</span>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statValue}>
                  {stats.following_count || 0}
                </span>
                <span className={styles.statLabel}>Подписки</span>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statValue}>
                  {stats.comments_count || 0}
                </span>
                <span className={styles.statLabel}>Комментарии</span>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statValue}>
                  {stats.collections_count || 0}
                </span>
                <span className={styles.statLabel}>Подборки</span>
              </div>
              <div className={styles.statCard}>
                <span className={styles.statValue}>
                  {stats.total_recipe_likes || 0}
                </span>
                <span className={styles.statLabel}>Лайки</span>
              </div>
            </div>
          </div>

          <div className={styles.tabsRow}>
            <button
              type="button"
              className={cn(styles.tabBtn, {
                [styles.tabBtnActive]: activeTab === "recipes",
              })}
              onClick={() => setActiveTab("recipes")}
            >
              Рецепты
            </button>

            <button
              type="button"
              className={cn(styles.tabBtn, {
                [styles.tabBtnActive]: activeTab === "collections",
              })}
              onClick={() => setActiveTab("collections")}
            >
              Подборки
            </button>

            <button
              type="button"
              className={cn(styles.tabBtn, {
                [styles.tabBtnActive]: activeTab === "comments",
              })}
              onClick={() => setActiveTab("comments")}
            >
              Комментарии
            </button>

            <button
              type="button"
              className={cn(styles.tabBtn, {
                [styles.tabBtnActive]: activeTab === "about",
              })}
              onClick={() => setActiveTab("about")}
            >
              О пользователе
            </button>
          </div>

          <div className={styles.tabContent}>
            {activeTab === "recipes" && (
              <div className={styles.contentCard}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>Рецепты пользователя</h2>

                  {is_owner && (
                    <Button
                      className={styles.createRecipeBtn}
                      modifier="style_dark"
                      href="/recipes/create"
                    >
                      <Icons.PlusIcon />
                      Создать рецепт
                    </Button>
                  )}
                </div>

                {recipes.length ? (
                  <div className={styles.recipeGrid}>
                    {recipes.map((recipe) => (
                      <Link
                        key={recipe.id}
                        to={`/recipes/${recipe.id}`}
                        className={styles.recipeCard}
                      >
                        <div className={styles.recipeImageWrap}>
                          {recipe.image ? (
                            <img
                              src={recipe.image}
                              alt={recipe.title}
                              className={styles.recipeImage}
                            />
                          ) : (
                            <div className={styles.recipeImagePlaceholder} />
                          )}
                        </div>

                        <div className={styles.recipeCardBody}>
                          <h3 className={styles.recipeTitle}>{recipe.title}</h3>

                          <div className={styles.recipeMeta}>
                            <span className={styles.recipeMetaItem}>
                              <Icons.ClockIcon />
                              {recipe.cooking_time_minutes} мин.
                            </span>

                            <span className={styles.recipeMetaItem}>
                              <span className={styles.recipeStar}>★</span>
                              {Number(recipe.rating_avg || 0).toFixed(1)}
                            </span>

                            <span className={styles.recipeMetaMuted}>
                              оценок: {recipe.rating_count || 0}
                            </span>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <div className={styles.placeholderBox}>
                    {is_owner
                      ? "У вас пока нет рецептов. Создайте первый рецепт."
                      : "У пользователя пока нет опубликованных рецептов"}
                  </div>
                )}
              </div>
            )}

            {activeTab === "collections" && (
              <div className={styles.contentCard}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>Подборки</h2>

                  {is_owner && (
                    <Button
                      className={styles.createRecipeBtn}
                      modifier="style_dark"
                      clickHandler={openCreateCollectionModal}
                    >
                      <Icons.PlusIcon />
                      Создать подборку
                    </Button>
                  )}
                </div>

                {collectionsLoading ? (
                  <div className={styles.placeholderBox}>Загрузка подборок...</div>
                ) : collections.length ? (
                  <div className={styles.collectionGrid}>
                    {collections.map((collection) => (
                      <div key={collection.id} className={styles.collectionCard}>
                        <div className={styles.collectionCardBody}>
                          <div className={styles.collectionCardTop}>
                            <div>
                              <h3 className={styles.collectionTitle}>
                                {collection.name}
                              </h3>
                              <div className={styles.collectionMeta}>
                                Рецептов: {collection.recipes_count || 0}
                              </div>
                            </div>
                          </div>

                          <div
                            className={cn(styles.collectionDescription, {
                              [styles.collectionDescriptionMuted]:
                                !collection.description,
                            })}
                          >
                            {collection.description ||
                              "Описание подборки не указано"}
                          </div>

                          <div className={styles.collectionFooter}>
                            <div className={styles.collectionInfo}>
                              <span className={styles.collectionDateLabel}>
                                Создана
                              </span>
                              <span className={styles.collectionDateValue}>
                                {formatCollectionDate(collection.created_at)}
                              </span>
                            </div>

                            <div className={styles.collectionActions}>
                              {is_owner && (
                                <>
                                  <Button
                                    className={styles.collectionSecondaryBtn}
                                    modifier="style_light"
                                    clickHandler={() =>
                                      openEditCollectionModal(collection)
                                    }
                                  >
                                    Редактировать
                                  </Button>

                                  <Button
                                    className={styles.collectionDangerBtn}
                                    modifier="style_light"
                                    clickHandler={() =>
                                      handleDeleteCollection(collection.id)
                                    }
                                  >
                                    Удалить
                                  </Button>
                                </>
                              )}

                              <Button
                                className={styles.collectionOpenBtn}
                                modifier="style_dark"
                                clickHandler={() =>
                                  history.push(`/collection/${collection.id}`)
                                }
                              >
                                Открыть подборку
                              </Button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className={styles.placeholderBox}>
                    {is_owner
                      ? "У вас пока нет подборок"
                      : "У пользователя пока нет подборок"}
                  </div>
                )}
              </div>
            )}

            {activeTab === "comments" && (
              <div className={styles.contentCard}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>Комментарии</h2>
                </div>

                {commentsLoading ? (
                  <div className={styles.placeholderBox}>Загрузка комментариев...</div>
                ) : comments.length ? (
                  <div className={styles.commentList}>
                    {comments.map((comment) => (
                      <div key={comment.id} className={styles.commentCard}>
                        <div className={styles.commentTop}>
                          <div className={styles.commentRecipeBlock}>
                            <span className={styles.commentRecipeTitle}>
                              {comment.recipe?.title || "Рецепт"}
                            </span>
                            <span className={styles.commentRecipeSubtitle}>
                              Комментарий к рецепту
                            </span>
                          </div>

                          <div className={styles.commentMeta}>
                            {formatCommentDate(comment.created_at)}
                          </div>
                        </div>

                        <div className={styles.commentText}>{comment.text}</div>

                        <div className={styles.commentBottom}>
                          <span className={styles.commentMeta}>
                            Лайков: {comment.likes_count || 0}
                          </span>

                          {comment.recipe?.id && (
                            <Link
                              to={`/recipes/${comment.recipe.id}`}
                              className={styles.commentOpenLink}
                            >
                              Перейти к рецепту
                            </Link>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className={styles.placeholderBox}>
                    {is_owner
                      ? "У вас пока нет комментариев"
                      : "У пользователя пока нет комментариев"}
                  </div>
                )}
              </div>
            )}

            {activeTab === "about" && (
              <div className={styles.contentCard}>
                <div className={styles.sectionHeader}>
                  <h2 className={styles.sectionTitle}>О пользователе</h2>
                </div>

                <div className={styles.aboutGrid}>
                  <div className={styles.aboutItem}>
                    <span className={styles.aboutLabel}>Имя</span>
                    <span className={styles.aboutValue}>{fullName}</span>
                  </div>

                  <div className={styles.aboutItem}>
                    <span className={styles.aboutLabel}>Username</span>
                    <span className={styles.aboutValue}>@{username}</span>
                  </div>

                  <div className={styles.aboutItem}>
                    <span className={styles.aboutLabel}>Статус</span>
                    <span className={styles.aboutValue}>
                      {status || "Не указан"}
                    </span>
                  </div>

                  <div className={styles.aboutItem}>
                    <span className={styles.aboutLabel}>Дата регистрации</span>
                    <span className={styles.aboutValue}>
                      {formatJoinDate(created_at)}
                    </span>
                  </div>

                  <div className={styles.aboutItemFull}>
                    <span className={styles.aboutLabel}>Описание</span>
                    <span
                      className={cn(styles.aboutValue, {
                        [styles.aboutValueMuted]: !bio,
                      })}
                    >
                      {bio || "Описание пока не заполнено"}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <CollectionModal
          isOpen={isCollectionModalOpen}
          title={editingCollection ? "Редактировать подборку" : "Создать подборку"}
          submitText={editingCollection ? "Сохранить" : "Создать"}
          initialValues={{
            name: editingCollection?.name || "",
            description: editingCollection?.description || "",
          }}
          loading={collectionSaving}
          onClose={closeCollectionModal}
          onSubmit={handleSubmitCollection}
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

export default ProfilePage;