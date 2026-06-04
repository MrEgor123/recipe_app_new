import { useEffect, useState } from "react";
import { Link, useHistory, useParams } from "react-router-dom";
import MetaTags from "react-meta-tags";

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

const formatDate = (value) => {
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

const normalizeImageSrc = (value) => {
  if (!value) return "";
  if (value.startsWith("data:image")) return value;
  if (value.startsWith("/media/") || value.startsWith("http")) return value;
  return `data:image/jpeg;base64,${value}`;
};

const CollectionDetailPage = () => {
  const history = useHistory();
  const { id } = useParams();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [collection, setCollection] = useState(null);
  const [recipes, setRecipes] = useState([]);
  const [isOwner, setIsOwner] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [notificationError, setNotificationError] = useState({
    text: "",
    position: "-100%",
  });

  const getBackUrl = () => {
    if (!collection) return "/recipes";
    if (collection.is_owner || isOwner) return "/profile";
    if (collection.user_id) return `/users/${collection.user_id}`;
    return "/recipes";
  };

  const goBackToOwnerProfile = () => {
    history.push(getBackUrl());
  };

  useEffect(() => {
    if (!id) {
      setLoading(false);
      setCollection(null);
      return;
    }

    setLoading(true);
    setCollection(null);

    Promise.all([
      api.getCollection({ collection_id: id }),
      api.getCollectionRecipes({ collection_id: id }).catch(() => []),
    ])
      .then(([collectionData, recipesData]) => {
        const normalizedRecipes = Array.isArray(recipesData) ? recipesData : [];

        setCollection(collectionData);
        setRecipes(normalizedRecipes);
        setIsOwner(Boolean(collectionData.is_owner));
      })
      .catch((err) => {
        console.log(err);
        setCollection(null);
        setRecipes([]);
        setIsOwner(false);
        setNotificationError({
          text: "Не удалось загрузить подборку",
          position: "40px",
        });
      })
      .finally(() => setLoading(false));
  }, [id]);

  const handleErrorClose = () => {
    setNotificationError((prev) => ({ ...prev, position: "-100%" }));
  };

  const handleDeleteCollection = () => {
    if (!collection) return;
    if (!window.confirm("Удалить подборку?")) return;

    api
      .deleteCollection({ collection_id: collection.id })
      .then(() => {
        history.push("/profile");
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось удалить подборку",
          position: "40px",
        });
      });
  };

  const handleRemoveRecipe = (recipeId) => {
    if (!collection || !recipeId) return;
    if (!window.confirm("Удалить рецепт из подборки?")) return;

    api
      .removeRecipeFromCollection({
        collection_id: collection.id,
        recipe_id: recipeId,
      })
      .then(() => {
        setRecipes((prev) =>
          prev.filter((recipe) => Number(recipe.id) !== Number(recipeId))
        );

        setCollection((prev) =>
          prev
            ? {
                ...prev,
                recipes_count: Math.max(Number(prev.recipes_count || 0) - 1, 0),
              }
            : prev
        );
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось удалить рецепт из подборки",
          position: "40px",
        });
      });
  };

  const handleUpdateCollection = ({ name, description }) => {
    if (!collection) return;

    setSaving(true);

    api
      .updateCollection({
        collection_id: collection.id,
        name,
        description,
      })
      .then((updatedCollection) => {
        setCollection(updatedCollection);
        setIsOwner(Boolean(updatedCollection.is_owner));
        setIsEditModalOpen(false);
      })
      .catch((err) => {
        console.log(err);
        setNotificationError({
          text: "Не удалось обновить подборку",
          position: "40px",
        });
      })
      .finally(() => setSaving(false));
  };

  if (loading) {
    return (
      <Main>
        <Container>
          <div className={styles.page}>
            <div className={styles.emptyCard}>Загрузка подборки...</div>
          </div>
        </Container>
      </Main>
    );
  }

  if (!collection) {
    return (
      <Main>
        <Container>
          <div className={styles.page}>
            <div className={styles.emptyCard}>
              <h1 className={styles.emptyTitle}>Подборка не найдена</h1>
              <p className={styles.emptyText}>
                Не удалось загрузить данные подборки
              </p>
              <Button
                className={styles.backBtn}
                modifier="style_dark"
                clickHandler={() => history.push("/recipes")}
              >
                Назад
              </Button>
            </div>
          </div>
        </Container>
      </Main>
    );
  }

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>{collection.name}</title>
          <meta
            name="description"
            content={`Recepto - подборка ${collection.name}`}
          />
          <meta property="og:title" content={collection.name} />
        </MetaTags>

        <div className={styles.page}>
          <div className={styles.card}>
            <div className={styles.header}>
              <div>
                <h1 className={styles.title}>{collection.name}</h1>
                <div className={styles.meta}>
                  <span>Рецептов: {collection.recipes_count || recipes.length}</span>
                  <span className={styles.dot} />
                  <span>Создана: {formatDate(collection.created_at)}</span>
                </div>
              </div>

              <div className={styles.actions}>
                {isOwner && (
                  <>
                    <Button
                      className={styles.actionBtn}
                      modifier="style_light"
                      clickHandler={() => setIsEditModalOpen(true)}
                    >
                      Редактировать
                    </Button>

                    <Button
                      className={styles.deleteBtn}
                      modifier="style_light"
                      clickHandler={handleDeleteCollection}
                    >
                      Удалить
                    </Button>
                  </>
                )}

                <Button
                  className={styles.actionBtn}
                  modifier="style_light"
                  clickHandler={goBackToOwnerProfile}
                >
                  Назад
                </Button>
              </div>
            </div>

            <div className={styles.description}>
              {collection.description || "Описание подборки не указано"}
            </div>
          </div>

          <div className={styles.contentCard}>
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>Рецепты в подборке</h2>
            </div>

            {recipes.length ? (
              <div className={styles.recipeGrid}>
                {recipes.map((recipe) => (
                  <div key={recipe.id} className={styles.recipeCard}>
                    <Link
                      to={`/recipes/${recipe.id}`}
                      className={styles.recipeCardLink}
                    >
                      <div className={styles.recipeImageWrap}>
                        {recipe.image ? (
                          <img
                            src={normalizeImageSrc(recipe.image)}
                            alt={recipe.title || recipe.name}
                            className={styles.recipeImage}
                          />
                        ) : (
                          <div className={styles.recipeImagePlaceholder} />
                        )}
                      </div>

                      <div className={styles.recipeCardBody}>
                        <h3 className={styles.recipeTitle}>
                          {recipe.title || recipe.name}
                        </h3>

                        <div className={styles.recipeMeta}>
                          <span className={styles.recipeMetaItem}>
                            <Icons.ClockIcon />
                            {recipe.cooking_time_minutes || recipe.cooking_time} мин.
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

                    {isOwner && (
                      <div className={styles.recipeCardFooter}>
                        <Button
                          className={styles.removeRecipeBtn}
                          modifier="style_light"
                          clickHandler={() => handleRemoveRecipe(recipe.id)}
                        >
                          Удалить из подборки
                        </Button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className={styles.emptyRecipes}>
                В этой подборке пока нет рецептов
              </div>
            )}
          </div>
        </div>

        <CollectionModal
          isOpen={isEditModalOpen}
          title="Редактировать подборку"
          submitText="Сохранить"
          initialValues={{
            name: collection.name || "",
            description: collection.description || "",
          }}
          loading={saving}
          onClose={() => {
            if (!saving) {
              setIsEditModalOpen(false);
            }
          }}
          onSubmit={handleUpdateCollection}
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

export default CollectionDetailPage;