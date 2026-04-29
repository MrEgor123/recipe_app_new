import { useEffect, useState } from "react";
import { useHistory } from "react-router-dom";
import MetaTags from "react-meta-tags";

import { Container, Main, Button } from "../../components";
import { Notification } from "../../components/notification";
import api from "../../api";
import styles from "./styles.module.css";

const ProfileEditPage = () => {
  const history = useHistory();

  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");
  const [bio, setBio] = useState("");
  const [coverImage, setCoverImage] = useState("");
  const [saving, setSaving] = useState(false);

  const [notification, setNotification] = useState({
    text: "",
    position: "-100%",
  });

  useEffect(() => {
    api
      .getMyProfile()
      .then((profile) => {
        setStatus(profile.status || "");
        setBio(profile.bio || "");
        setCoverImage(profile.cover_image || "");
      })
      .catch((err) => {
        console.log(err);
        setNotification({
          text: "Не удалось загрузить профиль",
          position: "40px",
        });
      })
      .finally(() => setLoading(false));
  }, []);

  const handleCloseNotification = () => {
    setNotification((prev) => ({ ...prev, position: "-100%" }));
  };

  const toBase64 = (file) =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
    });

  const handleCoverChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const base64 = await toBase64(file);
      setCoverImage(base64);
    } catch (err) {
      console.log(err);
      setNotification({
        text: "Не удалось загрузить изображение",
        position: "40px",
      });
    }
  };

  const handleRemoveCover = () => {
    setCoverImage("");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (saving) return;

    setSaving(true);

    api
      .updateMyProfile({
        status: status.trim() || null,
        bio: bio.trim() || null,
        cover_image: coverImage || null,
      })
      .then(() => {
        history.push("/profile");
      })
      .catch((err) => {
        console.log(err);
        setNotification({
          text: "Не удалось сохранить профиль",
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
            <div className={styles.card}>Загрузка...</div>
          </div>
        </Container>
      </Main>
    );
  }

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Редактировать профиль</title>
          <meta name="description" content="Редактирование профиля Recepto" />
        </MetaTags>

        <div className={styles.page}>
          <form className={styles.card} onSubmit={handleSubmit}>
            <div className={styles.header}>
              <h1 className={styles.title}>Редактировать профиль</h1>
              <p className={styles.subtitle}>
                Обновите статус, описание и баннер профиля
              </p>
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="status">
                Статус
              </label>
              <input
                id="status"
                type="text"
                className={styles.input}
                placeholder="Например: Люблю готовить домашнюю еду"
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                maxLength={120}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="bio">
                Описание
              </label>
              <textarea
                id="bio"
                className={styles.textarea}
                placeholder="Расскажите немного о себе"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                maxLength={2000}
              />
            </div>

            <div className={styles.formGroup}>
              <label className={styles.label} htmlFor="cover-file">
                Баннер профиля
              </label>

              <div className={styles.uploadRow}>
                <label htmlFor="cover-file" className={styles.uploadBtn}>
                  Выбрать изображение
                </label>

                {coverImage && (
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={handleRemoveCover}
                  >
                    Удалить баннер
                  </button>
                )}
              </div>

              <input
                id="cover-file"
                type="file"
                accept="image/*"
                className={styles.fileInput}
                onChange={handleCoverChange}
              />
            </div>

            <div className={styles.previewBlock}>
              <div className={styles.previewLabel}>Предпросмотр баннера</div>
              <div
                className={styles.previewCover}
                style={
                  coverImage
                    ? { backgroundImage: `url(${coverImage})` }
                    : undefined
                }
              >
                {!coverImage && (
                  <div className={styles.previewPlaceholder}>
                    Баннер пока не задан
                  </div>
                )}
              </div>
            </div>

            <div className={styles.actions}>
              <Button
                className={styles.cancelBtn}
                modifier="style_light"
                type="button"
                clickHandler={() => history.push("/profile")}
              >
                Отмена
              </Button>

              <Button
                className={styles.saveBtn}
                modifier="style_dark"
                type="submit"
                disabled={saving}
              >
                {saving ? "Сохранение..." : "Сохранить"}
              </Button>
            </div>
          </form>
        </div>

        <Notification
          text={notification.text}
          style={{ right: notification.position }}
          onClose={handleCloseNotification}
        />
      </Container>
    </Main>
  );
};

export default ProfileEditPage;