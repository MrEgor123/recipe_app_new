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
import { useRouteMatch, useParams, useHistory } from "react-router-dom";
import MetaTags from "react-meta-tags";
import DefaultImage from "../../images/userpic-icon.jpg";
import { useRecipe } from "../../utils/index.js";
import api from "../../api";
import { Notification } from "../../components/notification";

const SingleCard = ({ updateOrders }) => {
  const [loading, setLoading] = useState(true);
  const [notificationPosition, setNotificationPosition] = useState("-100%");
  const [notificationError, setNotificationError] = useState({
    text: "",
    position: "-100%",
  });

  const { recipe, setRecipe, handleLike, handleAddToCart, handleSubscribe } =
    useRecipe();

  const authContext = useContext(AuthContext);
  const userContext = useContext(UserContext);
  const { id } = useParams();
  const history = useHistory();
  const { url } = useRouteMatch();

  const handleCopyLink = () => {
    api
      .copyRecipeLink({ id })
      .then(({ "short-link": shortLink }) => {
        navigator.clipboard
          .writeText(shortLink)
          .then(() => {
            setNotificationPosition("40px");
            setTimeout(() => {
              setNotificationPosition("-100%");
            }, 3000);
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

  useEffect(() => {
    api
      .getRecipe({ recipe_id: id })
      .then((res) => {
        setRecipe(res);
        setLoading(false);
      })
      .catch(() => {
        history.push("/not-found");
      });
  }, []);

  const {
    author = {},
    image,
    tags,
    cooking_time,
    name,
    ingredients,
    text,
    is_favorited,
    is_in_shopping_cart,
  } = recipe;

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>{name}</title>
          <meta name="description" content={`Recepto - ${name}`} />
          <meta property="og:title" content={name} />
        </MetaTags>

        <div className={styles.page}>
          <div className={styles.layout}>
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
                    href={`/user/${author.id}`}
                    className={styles.authorLink}
                  />
                </div>
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

              <div className={styles.section}>
                <div className={cn(styles.card, styles.ingredientsCard)}>
                  <Ingredients ingredients={ingredients} />
                </div>
              </div>

              <div className={styles.section}>
                <div className={styles.card}>
                  <Description description={text} />
                </div>
              </div>
            </div>
          </div>
        </div>

        <Notification
          text="Ссылка скопирована"
          style={{ right: notificationPosition }}
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