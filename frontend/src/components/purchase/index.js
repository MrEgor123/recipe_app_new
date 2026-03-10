import styles from './styles.module.css'
import { LinkComponent, Icons, Popup } from '../index'
import { useState } from 'react'
import cn from 'classnames'

const Purchase = ({
  image,
  name,
  cooking_time,
  id,
  handleRemoveFromCart,
  is_in_shopping_cart,
  updateOrders,
  ingredients
}) => {
  const [expanded, setExpanded] = useState(false)
  const [toDelete, setToDelete] = useState(false)

  if (!is_in_shopping_cart) {
    return null
  }

  return (
    <li className={styles.purchase}>
      {toDelete && (
        <Popup
          title='Вы уверены, что хотите удалить рецепт?'
          onSubmit={() => {
            handleRemoveFromCart({
              id,
              toAdd: false,
              callback: () => {
                updateOrders()
                setToDelete(false)
              }
            })
          }}
          onClose={() => {
            setToDelete(false)
          }}
        />
      )}

      <div className={styles.purchaseBody}>
        <div className={styles.purchaseContent}>
          <div
            className={styles.purchaseImage}
            style={{ backgroundImage: `url(${image})` }}
          />

          <div className={styles.purchaseInfo}>
            <div className={styles.purchaseTopRow}>
              <h3 className={styles.purchaseTitle}>
                <LinkComponent
                  className={styles.recipeLink}
                  title={name}
                  href={`/recipes/${id}`}
                />
              </h3>

              {ingredients && ingredients.length > 0 && (
                <button
                  type="button"
                  className={cn(styles.purchaseExpandButton, {
                    [styles.purchaseExpandButtonExpanded]: expanded
                  })}
                  onClick={() => setExpanded(!expanded)}
                >
                  <Icons.ArrowExpand />
                </button>
              )}
            </div>

            <p className={styles.purchaseText}>
              {cooking_time} мин.
            </p>
          </div>
        </div>

        <button
          type="button"
          className={styles.purchaseDelete}
          onClick={() => setToDelete(true)}
          aria-label="Удалить рецепт из списка покупок"
        >
          <Icons.ReceiptDelete />
        </button>
      </div>

      {expanded && ingredients && ingredients.length > 0 && (
        <ul className={styles.purchaseIngredients}>
          {ingredients.map((ingredient, index) => (
            <li key={`${ingredient.name}-${index}`} className={styles.purchaseIngredient}>
              {ingredient.name}
            </li>
          ))}
        </ul>
      )}
    </li>
  )
}

export default Purchase