import { useEffect, useMemo, useState } from "react";
import MetaTags from "react-meta-tags";
import { toast } from "react-toastify";

import { Container, Main, Title, Button } from "../../components";
import api from "../../api";
import styles from "./styles.module.css";

const ShoppingCartPage = () => {
  const [loading, setLoading] = useState(true);
  const [markets, setMarkets] = useState([]);
  const [ingredients, setIngredients] = useState([]);
  const [summary, setSummary] = useState({});
  const [selectedMarketId, setSelectedMarketId] = useState("pyaterochka");

  useEffect(() => {
    setLoading(true);

    api
      .getShoppingCartMarket()
      .then((data) => {
        const loadedMarkets = Array.isArray(data.markets) ? data.markets : [];
        const loadedIngredients = Array.isArray(data.ingredients)
          ? data.ingredients
          : [];
        const loadedSummary = data.summary || {};

        setMarkets(loadedMarkets);
        setIngredients(loadedIngredients);
        setSummary(loadedSummary);

        if (loadedMarkets.length) {
          setSelectedMarketId((prev) => {
            const exists = loadedMarkets.some((market) => market.id === prev);
            return exists ? prev : loadedMarkets[0].id;
          });
        }
      })
      .catch((err) => {
        console.log(err);
        toast.error("Не удалось загрузить список покупок");
      })
      .finally(() => setLoading(false));
  }, []);

  const selectedMarket = useMemo(() => {
    return markets.find((market) => market.id === selectedMarketId) || markets[0];
  }, [markets, selectedMarketId]);

  const selectedSummary = useMemo(() => {
    return summary?.[selectedMarketId] || null;
  }, [summary, selectedMarketId]);

  const bestMarketId = useMemo(() => {
    const pricedMarkets = markets
      .map((market) => summary?.[market.id])
      .filter((item) => item && item.priced_count > 0);

    if (!pricedMarkets.length) {
      return null;
    }

    const best = pricedMarkets.reduce((min, item) => {
      return Number(item.estimated_total) < Number(min.estimated_total)
        ? item
        : min;
    });

    return best.market_id;
  }, [markets, summary]);

  const handleOpenProduct = (ingredient) => {
    const product = ingredient.market_products?.[selectedMarketId];
    const url = product?.product_url || ingredient.market_links?.[selectedMarketId];

    if (!url) {
      toast.error("Не удалось сформировать ссылку на магазин");
      return;
    }

    window.open(url, "_blank", "noopener,noreferrer");
  };

  const handleOpenMarket = () => {
    if (!selectedMarket?.home_url) {
      toast.error("Не удалось открыть выбранный магазин");
      return;
    }

    window.open(selectedMarket.home_url, "_blank", "noopener,noreferrer");
  };

  const handleDownloadTxt = () => {
    api
      .downloadShoppingListTxt()
      .then(() => {
        toast.success("Список покупок скачан");
      })
      .catch((err) => {
        console.log(err);
        toast.error("Не удалось скачать список покупок");
      });
  };

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Список покупок</title>
          <meta
            name="description"
            content="Recepto - список покупок по выбранным рецептам"
          />
        </MetaTags>

        <div className={styles.page}>
          <div className={styles.hero}>
            <div>
              <Title title="Список покупок" />

              <p className={styles.heroText}>
                Здесь собраны ингредиенты из рецептов, добавленных в список
                покупок. Выберите магазин и посмотрите примерную стоимость.
              </p>
            </div>

            <div className={styles.heroActions}>
              <Button
                modifier="style_light"
                className={styles.actionBtn}
                clickHandler={handleDownloadTxt}
              >
                Скачать .txt
              </Button>

              <Button
                modifier="style_dark"
                className={styles.actionBtn}
                clickHandler={handleOpenMarket}
                disabled={!selectedMarket}
              >
                Перейти к покупкам
              </Button>
            </div>
          </div>

          <div className={styles.marketCard}>
            <div className={styles.marketHeader}>
              <h2 className={styles.sectionTitle}>Выберите магазин</h2>

              {selectedMarket && (
                <span className={styles.selectedMarket}>
                  выбран: {selectedMarket.name}
                </span>
              )}
            </div>

            <div className={styles.marketsGrid}>
              {markets.map((market) => {
                const marketSummary = summary?.[market.id];
                const isBest = bestMarketId === market.id;

                return (
                  <button
                    key={market.id}
                    type="button"
                    className={`${styles.marketBtn} ${
                      selectedMarketId === market.id ? styles.marketBtnActive : ""
                    } ${isBest ? styles.marketBtnBest : ""}`}
                    onClick={() => setSelectedMarketId(market.id)}
                  >
                    <div className={styles.marketTop}>
                      <span className={styles.marketName}>{market.name}</span>

                      {isBest && (
                        <span className={styles.bestBadge}>выгоднее</span>
                      )}
                    </div>

                    <span className={styles.marketDescription}>
                      {market.description}
                    </span>

                    {marketSummary && (
                      <span className={styles.marketPrice}>
                        ≈ {marketSummary.estimated_total_text} ₽ · найдено{" "}
                        {marketSummary.priced_count}/{marketSummary.total_count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {selectedSummary && (
            <div className={styles.summaryCard}>
              <div>
                <div className={styles.summaryLabel}>
                  ориентировочная стоимость
                </div>

                <div className={styles.summaryPrice}>
                  ≈ {selectedSummary.estimated_total_text}₽
                </div>
              </div>

              <div className={styles.summaryStats}>
                цены найдены: {selectedSummary.priced_count}/
                {selectedSummary.total_count}
              </div>
            </div>
          )}

          <div className={styles.listCard}>
            <div className={styles.listHeader}>
              <div>
                <h2 className={styles.sectionTitle}>Ингредиенты</h2>

                <p className={styles.sectionText}>
                  Количество уже суммировано по всем рецептам в списке.
                </p>
              </div>

              <div className={styles.countBadge}>
                позиций: {ingredients.length}
              </div>
            </div>

            {loading ? (
              <div className={styles.emptyBox}>Загрузка списка покупок...</div>
            ) : ingredients.length ? (
              <div className={styles.ingredientsList}>
                {ingredients.map((ingredient) => {
                  const product = ingredient.market_products?.[selectedMarketId];

                  return (
                    <div key={ingredient.id} className={styles.ingredientItem}>
                      <div className={styles.ingredientMain}>
                        <div className={styles.ingredientInfo}>
                          <div className={styles.ingredientName}>
                            {ingredient.name}
                          </div>

                          <div className={styles.ingredientAmount}>
                            нужно: {ingredient.amount_text} {ingredient.unit}
                          </div>
                        </div>

                        {product ? (
                          <div className={styles.priceBox}>
                            <div className={styles.productName}>
                              {product.product_name}
                            </div>

                            <div className={styles.productMeta}>
                              упаковка: {product.package_amount_text}{" "}
                              {product.package_unit} · цена:{" "}
                              {product.price_text} ₽
                            </div>

                            <div className={styles.productTotal}>
                              нужно упаковок: {product.packages_count} · примерно:{" "}
                              {product.estimated_price_text} ₽
                            </div>
                          </div>
                        ) : (
                          <div className={styles.priceBoxEmpty}>
                            <span className={styles.priceLabel}>цена</span>
                            <span className={styles.priceEmpty}>
                              нет данных по выбранному магазину
                            </span>
                          </div>
                        )}
                      </div>

                      <Button
                        modifier="style_light"
                        className={styles.findBtn}
                        clickHandler={() => handleOpenProduct(ingredient)}
                      >
                        Найти в магазине
                      </Button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className={styles.emptyBox}>
                Список покупок пуст. Добавьте рецепты в список покупок, чтобы
                здесь появились ингредиенты.
              </div>
            )}
          </div>

          <div className={styles.infoCard}>
            <h2 className={styles.infoTitle}>Как это работает?</h2>

            <p className={styles.infoText}>
              Приложение берет ингредиенты из списка покупок, ищет для них
              сохраненные товары из таблицы market_products и считает примерную
              стоимость с учетом количества упаковок. Самый выгодный магазин
              подсвечивается автоматически.
            </p>

            <div className={styles.noteBox}>
              <div className={styles.noteTitle}>Важно</div>

              <div className={styles.noteText}>
                Цены являются ориентировочными и используются для
                предварительного сравнения магазинов. Данные о товарах и
                стоимости хранятся в базе приложения и могут отличаться от
                актуальных цен на сайте магазина.
              </div>
            </div>
          </div>
        </div>
      </Container>
    </Main>
  );
};

export default ShoppingCartPage;