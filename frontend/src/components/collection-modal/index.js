import { useEffect, useState } from "react";
import { Button } from "../index";
import styles from "./styles.module.css";

const CollectionModal = ({
  isOpen,
  title = "Подборка",
  submitText = "Сохранить",
  initialValues = { name: "", description: "" },
  loading = false,
  onClose,
  onSubmit,
}) => {
  const [name, setName] = useState(initialValues.name || "");
  const [description, setDescription] = useState(initialValues.description || "");

  useEffect(() => {
    if (!isOpen) return;
    setName(initialValues.name || "");
    setDescription(initialValues.description || "");
  }, [isOpen, initialValues]);

  if (!isOpen) {
    return null;
  }

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim() || loading) return;

    onSubmit({
      name: name.trim(),
      description: description.trim(),
    });
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          <button
            type="button"
            className={styles.closeBtn}
            onClick={onClose}
            aria-label="Закрыть"
          >
            ×
          </button>
        </div>

        <form className={styles.form} onSubmit={handleSubmit}>
          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="collection-name">
              Название
            </label>
            <input
              id="collection-name"
              type="text"
              className={styles.input}
              placeholder="Введите название подборки"
              maxLength={100}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.label} htmlFor="collection-description">
              Описание
            </label>
            <textarea
              id="collection-description"
              className={styles.textarea}
              placeholder="Введите описание подборки"
              maxLength={500}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className={styles.footer}>
            <Button
              className={styles.cancelBtn}
              modifier="style_light"
              type="button"
              clickHandler={onClose}
            >
              Отмена
            </Button>

            <Button
              className={styles.submitBtn}
              modifier="style_dark"
              type="submit"
              disabled={!name.trim() || loading}
            >
              {loading ? "Сохранение..." : submitText}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CollectionModal;