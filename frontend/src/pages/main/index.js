import {
  Card,
  Title,
  Pagination,
  CardList,
  Container,
  Main,
  CheckboxGroup
} from '../../components'
import styles from './styles.module.css'
import { useRecipes } from '../../utils/index.js'
import { useEffect, useContext } from 'react'
import api from '../../api'
import MetaTags from 'react-meta-tags'
import { AuthContext } from '../../contexts'

const HomePage = ({ updateOrders }) => {
  const authContext = useContext(AuthContext)

  const {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    setTagsValue,
    handleTagsChange,
    handleLike,
    handleAddToCart
  } = useRecipes()

  const getRecipes = ({ page = 1, tags }) => {
    api.getRecipes({ page, tags })
      .then(res => {
        const { results, count } = res
        setRecipes(results)
        setRecipesCount(count)
      })
      .catch(() => {
        setRecipes([])
        setRecipesCount(0)
      })
  }

  useEffect(() => {
    getRecipes({ page: recipesPage, tags: tagsValue })
  }, [recipesPage, tagsValue, authContext])

  useEffect(() => {
    api.getTags().then(tags => {
      setTagsValue(tags.map(tag => ({ ...tag, value: false })))
    })
  }, [])

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>Рецепты</title>
          <meta name="description" content="Recepto - Рецепты" />
          <meta property="og:title" content="Рецепты" />
        </MetaTags>

        <div className={styles.title}>
          <div className={styles.titleLeft}>
            <Title title="Рецепты" />
          </div>

          <div className={styles.titleRight}>
            <CheckboxGroup
              values={tagsValue}
              handleChange={value => {
                setRecipesPage(1)
                handleTagsChange(value)
              }}
            />
          </div>
        </div>

        {recipes.length > 0 && (
          <CardList>
            {recipes.map(card => (
              <Card
                {...card}
                key={card.id}
                updateOrders={updateOrders}
                handleLike={handleLike}
                handleAddToCart={handleAddToCart}
              />
            ))}
          </CardList>
        )}

        <Pagination
          count={recipesCount}
          limit={6}
          page={recipesPage}
          onPageChange={page => setRecipesPage(page)}
        />
      </Container>
    </Main>
  )
}

export default HomePage