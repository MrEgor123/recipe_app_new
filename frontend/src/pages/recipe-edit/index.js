import {
  Container,
  IngredientsSearch,
  FileInput,
  Input,
  Title,
  CheckboxGroup,
  Main,
  Form,
  Button,
  Textarea,
} from "../../components";
import styles from "./styles.module.css";
import api from "../../api";
import { useEffect, useState } from "react";
import { useTags } from "../../utils";
import { useParams, useHistory } from "react-router-dom";
import MetaTags from "react-meta-tags";
import { Icons } from "../../components";
import cn from "classnames";

const MAX_RECIPE_NAME_LENGTH = 120;
const MAX_RECIPE_TEXT_LENGTH = 5000;

const RecipeEdit = ({ onItemDelete }) => {
  const { value, handleChange, setValue } = useTags();
  const [recipeName, setRecipeName] = useState("");

  const [ingredientValue, setIngredientValue] = useState({
    name: "",
    id: null,
    amount: "",
    measurement_unit: "",
  });

  const [recipeIngredients, setRecipeIngredients] = useState([]);
  const [recipeText, setRecipeText] = useState("");
  const [recipeTime, setRecipeTime] = useState("");
  const [recipeFile, setRecipeFile] = useState(null);
  const [recipeFileWasManuallyChanged, setRecipeFileWasManuallyChanged] =
    useState(false);

  const [ingredients, setIngredients] = useState([]);
  const [showIngredients, setShowIngredients] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitError, setSubmitError] = useState({ submitError: "" });
  const [ingredientError, setIngredientError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const history = useHistory();
  const { id } = useParams();

  const clearErrors = () => {
    setSubmitError({ submitError: "" });
    setIngredientError("");
  };

  const handleIngredientAutofill = ({ id, name, measurement_unit }) => {
    setIngredientValue({
      ...ingredientValue,
      id,
      name,
      measurement_unit,
    });
  };

  const handleAddIngredient = () => {
    if (
      ingredientValue.amount === "" ||
      ingredientValue.name === "" ||
      !ingredientValue.id
    ) {
      setIngredientError("Ингредиент не выбран");
      return;
    }

    if (!/^\d+$/.test(String(ingredientValue.amount))) {
      setIngredientError("Введите корректное количество");
      return;
    }

    if (Number(ingredientValue.amount) <= 0) {
      setIngredientError("Количество должно быть больше 0");
      return;
    }

    if (recipeIngredients.find(({ id }) => id === ingredientValue.id)) {
      setIngredientError("Ингредиент уже выбран");
      return;
    }

    setRecipeIngredients([...recipeIngredients, ingredientValue]);
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

  useEffect(() => {
    if (ingredientValue.name === "") {
      setIngredients([]);
      return;
    }

    api.getIngredients({ name: ingredientValue.name }).then((ingredients) => {
      setIngredients(ingredients);
    });
  }, [ingredientValue.name]);

  useEffect(() => {
    api.getTags().then((tags) => {
      setValue(tags.map((tag) => ({ ...tag, value: true })));
    });
  }, [setValue]);

  useEffect(() => {
    if (value.length === 0 || !loading) {
      return;
    }

    api
      .getRecipe({
        recipe_id: id,
      })
      .then((res) => {
        const { image, tags, cooking_time, name, ingredients, text } = res;

        setRecipeText(text || "");
        setRecipeName(name || "");
        setRecipeTime(cooking_time || "");
        setRecipeFile(image);
        setRecipeIngredients(Array.isArray(ingredients) ? ingredients : []);

        const tagsValueUpdated = value.map((item) => ({
          ...item,
          value: Boolean((tags || []).find((tag) => tag.id === item.id)),
        }));

        setValue(tagsValueUpdated);
        setLoading(false);
      })
      .catch(() => {
        history.push("/recipes");
      });
  }, [value, loading, id, history, setValue]);

  const checkIfDisabled = () => {
    const name = recipeName.trim();
    const text = recipeText.trim();
    const time = Number(recipeTime);

    if (!name) {
      setSubmitError({ submitError: "Введите название рецепта" });
      return true;
    }

    if (name.length > MAX_RECIPE_NAME_LENGTH) {
      setSubmitError({
        submitError: `Название рецепта должно быть не длиннее ${MAX_RECIPE_NAME_LENGTH} символов`,
      });
      return true;
    }

    if (value.filter((item) => item.value).length === 0) {
      setSubmitError({ submitError: "Выберите хотя бы один тег" });
      return true;
    }

    if (recipeIngredients.length === 0) {
      setSubmitError({ submitError: "Добавьте хотя бы один ингредиент" });
      return true;
    }

    if (!recipeTime || Number.isNaN(time) || time <= 0) {
      setSubmitError({
        submitError: "Время приготовления должно быть положительным числом",
      });
      return true;
    }

    if (!Number.isInteger(time)) {
      setSubmitError({
        submitError: "Время приготовления должно быть целым числом",
      });
      return true;
    }

    if (!text) {
      setSubmitError({ submitError: "Введите описание рецепта" });
      return true;
    }

    if (text.length > MAX_RECIPE_TEXT_LENGTH) {
      setSubmitError({
        submitError: `Описание рецепта должно быть не длиннее ${MAX_RECIPE_TEXT_LENGTH} символов`,
      });
      return true;
    }

    if (!recipeFile) {
      setSubmitError({ submitError: "Загрузите фото рецепта" });
      return true;
    }

    return false;
  };

  const openRecipeAfterSave = () => {
    const targetUrl = `${window.location.origin}/recipes/${id}?updated=${Date.now()}`;
    window.location.replace(targetUrl);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (isSubmitting) {
      return;
    }

    clearErrors();

    if (checkIfDisabled()) {
      return;
    }

    setIsSubmitting(true);

    const data = {
      text: recipeText.trim(),
      name: recipeName.trim(),
      ingredients: recipeIngredients.map((item) => ({
        id: item.id,
        amount: Number(item.amount),
      })),
      tags: value.filter((item) => item.value).map((item) => item.id),
      cooking_time: Number(recipeTime),
      image: recipeFile,
      recipe_id: id,
    };

    api
      .updateRecipe(data, recipeFileWasManuallyChanged)
      .then(() => {
        openRecipeAfterSave();
      })
      .catch((err) => {
        setSubmitError({
          submitError:
            err?.message ||
            err?.submitError ||
            "Ошибка сохранения рецепта. Проверьте правильность заполнения формы",
        });
        setIsSubmitting(false);
      });
  };

  const handleDelete = () => {
    if (isSubmitting) {
      return;
    }

    api.deleteRecipe({ recipe_id: id }).then(() => {
      onItemDelete && onItemDelete();
      history.push("/recipes");
    });
  };

  if (loading) {
    return (
      <Main>
        <Container>
          <MetaTags>
            <title>Редактирование рецепта</title>
            <meta name="description" content="Recepto - Редактирование рецепта" />
            <meta property="og:title" content="Редактирование рецепта" />
          </MetaTags>

          <Title title="Редактирование рецепта" />
          <div>Загрузка...</div>
        </Container>
      </Main>
    );
  }

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Редактирование рецепта</title>
          <meta name="description" content="Recepto - Редактирование рецепта" />
          <meta property="og:title" content="Редактирование рецепта" />
        </MetaTags>

        <Title title="Редактирование рецепта" />

        <Form className={styles.form} onSubmit={handleSubmit}>
          <Input
            label="Название рецепта"
            onChange={(e) => {
              clearErrors();
              setRecipeName(e.target.value);
            }}
            value={recipeName}
            className={styles.mb36}
            maxLength={MAX_RECIPE_NAME_LENGTH}
          />

          <CheckboxGroup
            label="Теги"
            emptyText="Нет загруженных тегов"
            values={value}
            className={styles.checkboxGroup}
            labelClassName={styles.checkboxGroupLabel}
            tagsClassName={styles.checkboxGroupTags}
            checkboxClassName={styles.checkboxGroupItem}
            handleChange={handleChange}
          />

          <div className={styles.ingredients}>
            <div className={styles.ingredientsInputs}>
              <Input
                label="Ингредиенты"
                className={styles.ingredientsNameInput}
                inputClassName={styles.ingredientsInput}
                labelClassName={styles.ingredientsLabel}
                placeholder="Начните вводить название"
                onChange={(e) => {
                  clearErrors();
                  setIngredientValue({
                    ...ingredientValue,
                    id: null,
                    name: e.target.value,
                    measurement_unit: "",
                  });
                }}
                onFocus={() => {
                  setShowIngredients(true);
                }}
                value={ingredientValue.name}
              />

              <div className={styles.ingredientsAmountInputContainer}>
                <p className={styles.amountText}>в количестве </p>

                <Input
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      e.preventDefault();
                      handleAddIngredient();
                    }
                  }}
                  className={styles.ingredientsAmountInput}
                  inputClassName={styles.ingredientsAmountValue}
                  onChange={(e) => {
                    clearErrors();
                    setIngredientValue({
                      ...ingredientValue,
                      amount: e.target.value,
                    });
                  }}
                  placeholder={0}
                  value={ingredientValue.amount}
                  type="number"
                  min="1"
                />

                {ingredientValue.measurement_unit !== "" && (
                  <div className={styles.measurementUnit}>
                    {ingredientValue.measurement_unit}
                  </div>
                )}
              </div>

              {showIngredients && ingredients.length > 0 && (
                <IngredientsSearch
                  ingredients={ingredients}
                  onClick={({ id, name, measurement_unit }) => {
                    handleIngredientAutofill({ id, name, measurement_unit });
                    setIngredients([]);
                    setShowIngredients(false);
                  }}
                />
              )}
            </div>

            <div className={styles.ingredientAdd} onClick={handleAddIngredient}>
              Добавить ингредиент
            </div>

            {ingredientError && (
              <p className={cn(styles.error, styles.errorIngredient)}>
                {ingredientError}
              </p>
            )}

            <div className={styles.ingredientsAdded}>
              {recipeIngredients.map((item) => {
                return (
                  <div className={styles.ingredientsAddedItem} key={item.id}>
                    <span className={styles.ingredientsAddedItemTitle}>
                      {item.name}
                    </span>{" "}
                    <span>-</span>{" "}
                    <span>
                      {item.amount} {item.measurement_unit}
                    </span>{" "}
                    <span
                      className={styles.ingredientsAddedItemRemove}
                      onClick={() => {
                        const recipeIngredientsUpdated =
                          recipeIngredients.filter((ingredient) => {
                            return ingredient.id !== item.id;
                          });
                        setRecipeIngredients(recipeIngredientsUpdated);
                      }}
                    >
                      <Icons.IngredientDelete />
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          <div
            className={cn(
              styles.ingredientsAmountInputContainer,
              styles.ingredientsAmountInputContainerMob
            )}
          >
            <p className={styles.amountText}>в количестве </p>

            <Input
              className={styles.ingredientsAmountInput}
              inputClassName={styles.ingredientsAmountValue}
              onChange={(e) => {
                clearErrors();
                setIngredientValue({
                  ...ingredientValue,
                  amount: e.target.value,
                });
              }}
              placeholder={0}
              value={ingredientValue.amount}
              type="number"
              min="1"
            />

            {ingredientValue.measurement_unit !== "" && (
              <div className={styles.measurementUnit}>
                {ingredientValue.measurement_unit}
              </div>
            )}
          </div>

          <div className={styles.cookingTime}>
            <Input
              label="Время приготовления"
              className={styles.ingredientsTimeInput}
              labelClassName={styles.cookingTimeLabel}
              inputClassName={styles.ingredientsTimeValue}
              onChange={(e) => {
                clearErrors();
                setRecipeTime(e.target.value);
              }}
              placeholder="0"
              value={recipeTime}
              type="number"
              min="1"
            />

            <div className={styles.cookingTimeUnit}>мин.</div>
          </div>

          <Textarea
            label="Описание рецепта"
            onChange={(e) => {
              clearErrors();
              setRecipeText(e.target.value);
            }}
            value={recipeText}
            placeholder="Опишите действия"
            maxLength={MAX_RECIPE_TEXT_LENGTH}
          />

          <FileInput
            onChange={(file) => {
              clearErrors();
              setRecipeFileWasManuallyChanged(true);
              setRecipeFile(file);
            }}
            fileTypes={["image/png", "image/jpeg"]}
            fileSize={5000}
            className={styles.fileInput}
            label="Загрузить фото"
            file={recipeFile}
          />

          <div className={styles.actions}>
            <Button
              modifier="style_dark"
              type="submit"
              className={styles.button}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Сохранение..." : "Сохранить"}
            </Button>

            <div className={styles.deleteRecipe} onClick={handleDelete}>
              Удалить
            </div>
          </div>

          {submitError.submitError && (
            <p className={styles.error}>{submitError.submitError}</p>
          )}
        </Form>
      </Container>
    </Main>
  );
};

export default RecipeEdit;