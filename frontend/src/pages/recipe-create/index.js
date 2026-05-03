import {
  Container,
  IngredientsSearch,
  FileInput,
  Input,
  Title,
  CheckboxGroup,
  Main,
  Button,
  Textarea,
} from "../../components";

import styles from "./styles.module.css";
import api from "../../api";

import { useEffect, useState } from "react";
import { useTags } from "../../utils";
import { useHistory } from "react-router-dom";
import MetaTags from "react-meta-tags";
import { Icons } from "../../components";

import { toast } from "react-toastify";

const RecipeCreate = () => {
  const { value, handleChange, setValue } = useTags();
  const history = useHistory();

  const [recipeName, setRecipeName] = useState("");
  const [recipeText, setRecipeText] = useState("");
  const [recipeTime, setRecipeTime] = useState("");
  const [recipeFile, setRecipeFile] = useState(null);

  const [ingredientValue, setIngredientValue] = useState({
    name: "",
    id: null,
    amount: "",
    measurement_unit: "",
  });

  const [recipeIngredients, setRecipeIngredients] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [showIngredients, setShowIngredients] = useState(false);
  const [ingredientError, setIngredientError] = useState("");

  useEffect(() => {
    api.getTags().then((tags) => {
      setValue(tags.map((tag) => ({ ...tag, value: true })));
    });
  }, [setValue]);

  useEffect(() => {
    if (!ingredientValue.name) {
      setIngredients([]);
      return;
    }

    api.getIngredients({ name: ingredientValue.name }).then(setIngredients);
  }, [ingredientValue.name]);

  const handleIngredientAutofill = ({ id, name, measurement_unit }) => {
    setIngredientValue((prev) => ({
      ...prev,
      id,
      name,
      measurement_unit,
    }));
  };

  const handleAddIngredient = () => {
    if (!ingredientValue.id || !ingredientValue.name) {
      setIngredientError("Ингредиент не выбран");
      return;
    }

    if (!ingredientValue.amount || !/^\d+$/.test(ingredientValue.amount)) {
      setIngredientError("Введите корректное количество");
      return;
    }

    if (Number(ingredientValue.amount) <= 0) {
      setIngredientError("Количество должно быть больше 0");
      return;
    }

    if (recipeIngredients.find((item) => item.id === ingredientValue.id)) {
      setIngredientError("Ингредиент уже добавлен");
      return;
    }

    setRecipeIngredients((prev) => [...prev, ingredientValue]);

    setIngredientValue({
      name: "",
      id: null,
      amount: "",
      measurement_unit: "",
    });

    setIngredients([]);
    setShowIngredients(false);
    setIngredientError("");
  };

  const handleRemoveIngredient = (id) => {
    setRecipeIngredients((prev) => prev.filter((item) => item.id !== id));
  };

  const checkIfDisabled = () => {
    if (!recipeName.trim()) {
      toast.error("Введите название рецепта");
      return true;
    }

    if (!value.filter((tag) => tag.value).length) {
      toast.error("Выберите хотя бы один тег");
      return true;
    }

    if (recipeIngredients.length === 0) {
      toast.error("Добавьте хотя бы один ингредиент");
      return true;
    }

    if (!recipeTime || Number(recipeTime) <= 0) {
      toast.error("Введите корректное время приготовления");
      return true;
    }

    if (!recipeText.trim()) {
      toast.error("Введите описание рецепта");
      return true;
    }

    if (!recipeFile) {
      toast.error("Загрузите фото рецепта");
      return true;
    }

    return false;
  };

  const showModerationError = () => {
    toast.error(
      "Ваш рецепт не прошёл модерацию и не был опубликован. Если вы считаете, что это ошибка, напишите в поддержку: @MrEgorAP",
      {
        autoClose: 10000,
      }
    );
  };

  const showModerationPending = () => {
    toast.info(
      "Рецепт отправлен на модерацию. После проверки он появится на сайте",
      {
        autoClose: 8000,
      }
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (checkIfDisabled()) return;

    const data = {
      name: recipeName.trim(),
      text: recipeText.trim(),
      cooking_time: Number(recipeTime),
      image: recipeFile,
      ingredients: recipeIngredients.map((item) => ({
        id: item.id,
        amount: Number(item.amount),
      })),
      tags: value.filter((tag) => tag.value).map((tag) => tag.id),
    };

    api
      .createRecipe(data)
      .then((res) => {
        const moderationStatus = res?.moderation_status;
        const hasPublicationFlag = Object.prototype.hasOwnProperty.call(
          res || {},
          "is_published"
        );

        if (
          moderationStatus === "rejected" ||
          (hasPublicationFlag && res.is_published === false)
        ) {
          showModerationError();
          history.push("/recipes");
          return;
        }

        if (moderationStatus === "pending") {
          showModerationPending();
          history.push("/recipes");
          return;
        }

        toast.success("Рецепт успешно создан");

        if (res?.id) {
          history.push(`/recipes/${res.id}`);
          return;
        }

        history.push("/recipes");
      })
      .catch((err) => {
        console.log(err);

        toast.error(
          err?.detail ||
            err?.message ||
            "Ошибка создания рецепта"
        );
      });
  };

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Создание рецепта</title>
        </MetaTags>

        <Title title="Создание рецепта" />

        <form className={styles.form} onSubmit={handleSubmit}>
          <Input
            label="Название рецепта"
            value={recipeName}
            onChange={(e) => setRecipeName(e.target.value)}
            className={styles.mb36}
          />

          <CheckboxGroup
            label="Теги"
            values={value}
            emptyText="Нет тегов"
            handleChange={handleChange}
            className={styles.checkboxGroup}
            labelClassName={styles.checkboxGroupLabel}
            tagsClassName={styles.checkboxGroupTags}
            checkboxClassName={styles.checkboxGroupItem}
          />

          <div className={styles.ingredients}>
            <div className={styles.ingredientsInputs}>
              <div className={styles.ingredientsNameInput}>
                <Input
                  label="Ингредиенты"
                  placeholder="Начните вводить название"
                  value={ingredientValue.name}
                  onChange={(e) =>
                    setIngredientValue({
                      ...ingredientValue,
                      id: null,
                      name: e.target.value,
                      measurement_unit: "",
                    })
                  }
                  onFocus={() => setShowIngredients(true)}
                  inputClassName={styles.ingredientsInput}
                />

                {showIngredients && ingredients.length > 0 && (
                  <IngredientsSearch
                    ingredients={ingredients}
                    onClick={(item) => {
                      handleIngredientAutofill(item);
                      setShowIngredients(false);
                      setIngredients([]);
                    }}
                  />
                )}
              </div>

              <div className={styles.ingredientsAmountInputContainer}>
                <span className={styles.amountText}>в количестве</span>

                <Input
                  type="number"
                  value={ingredientValue.amount}
                  onChange={(e) =>
                    setIngredientValue({
                      ...ingredientValue,
                      amount: e.target.value,
                    })
                  }
                  inputClassName={styles.ingredientsAmountValue}
                  className={styles.ingredientsAmountInput}
                  min="1"
                />

                {ingredientValue.measurement_unit && (
                  <span className={styles.measurementUnit}>
                    {ingredientValue.measurement_unit}
                  </span>
                )}
              </div>
            </div>

            <div className={styles.ingredientAdd} onClick={handleAddIngredient}>
              Добавить ингредиент
            </div>

            {ingredientError && (
              <p className={`${styles.error} ${styles.errorIngredient}`}>
                {ingredientError}
              </p>
            )}

            {recipeIngredients.length > 0 && (
              <div className={styles.ingredientsAdded}>
                {recipeIngredients.map((item) => (
                  <div className={styles.ingredientsAddedItem} key={item.id}>
                    <span className={styles.ingredientsAddedItemTitle}>
                      {item.name}
                    </span>

                    <span>
                      {item.amount} {item.measurement_unit}
                    </span>

                    <span
                      className={styles.ingredientsAddedItemRemove}
                      onClick={() => handleRemoveIngredient(item.id)}
                    >
                      <Icons.IngredientDelete />
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className={styles.cookingTime}>
            <Input
              label="Время приготовления"
              type="number"
              value={recipeTime}
              onChange={(e) => setRecipeTime(e.target.value)}
              inputClassName={styles.ingredientsTimeValue}
              className={styles.ingredientsTimeInput}
              labelClassName={styles.cookingTimeLabel}
              min="1"
            />

            <span className={styles.cookingTimeUnit}>мин.</span>
          </div>

          <Textarea
            label="Описание рецепта"
            placeholder="Опишите действия"
            value={recipeText}
            onChange={(e) => setRecipeText(e.target.value)}
          />

          <FileInput
            label="Загрузить фото"
            onChange={setRecipeFile}
            className={styles.fileInput}
          />

          <Button
            type="submit"
            modifier="style_dark-blue"
            className={styles.button}
          >
            Создать рецепт
          </Button>
        </form>
      </Container>
    </Main>
  );
};

export default RecipeCreate;