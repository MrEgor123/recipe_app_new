class Api {
  constructor(url, headers) {
    this._url = url;
    this._headers = headers;
  }

  checkResponse(res) {
    if (res.status === 204 || res.status === 304) {
      return Promise.resolve({});
    }

    return res.text().then((text) => {
      let data = {};

      try {
        data = text ? JSON.parse(text) : {};
      } catch {
        data = {};
      }

      if (res.ok) {
        return data;
      }

      return Promise.reject(data);
    });
  }

  checkFileDownloadResponse(res) {
    if (!res.ok) {
      return Promise.reject({});
    }

    return res.blob().then((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "shopping-list";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      return {};
    });
  }

  signin({ email, password }) {
    return fetch("/api/auth/token/login/", {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({
        email,
        password,
      }),
    }).then((res) => this.checkResponse(res));
  }

  signout() {
    const token = localStorage.getItem("token");

    return fetch("/api/auth/token/logout/", {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  signup({ email, password, username, first_name, last_name }) {
    return fetch("/api/users/", {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({
        email,
        password,
        username,
        first_name,
        last_name,
      }),
    }).then((res) => this.checkResponse(res));
  }

  getUserData() {
    const token = localStorage.getItem("token");

    return fetch("/api/users/me/", {
      method: "GET",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getMyProfile() {
    const token = localStorage.getItem("token");

    return fetch("/users/me/profile/", {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getProfile({ user_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Bearer ${token}` } : {};

    return fetch(`/users/${user_id}/profile/`, {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  updateMyProfile({ status, bio, cover_image }) {
    const token = localStorage.getItem("token");
    const payload = {};

    if (status !== undefined) {
      payload.status = status;
    }

    if (bio !== undefined) {
      payload.bio = bio;
    }

    if (cover_image !== undefined) {
      payload.cover_image = cover_image;
    }

    return fetch("/users/me/profile/", {
      method: "PATCH",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    }).then((res) => this.checkResponse(res));
  }

  getMyCollectionsProfile() {
    const token = localStorage.getItem("token");

    return fetch("/users/me/collections/", {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getUserCollections({ user_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Bearer ${token}` } : {};

    return fetch(`/users/${user_id}/collections/`, {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  getMyProfileComments() {
    const token = localStorage.getItem("token");

    return fetch("/users/me/comments/", {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getUserProfileComments({ user_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Bearer ${token}` } : {};

    return fetch(`/users/${user_id}/comments/`, {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  changePassword({ current_password, new_password }) {
    const token = localStorage.getItem("token");

    return fetch("/api/users/set_password/", {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({ current_password, new_password }),
    }).then((res) => this.checkResponse(res));
  }

  changeAvatar({ file }) {
    const token = localStorage.getItem("token");

    return fetch("/api/users/me/avatar/", {
      method: "PUT",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({ avatar: file }),
    }).then((res) => this.checkResponse(res));
  }

  deleteAvatar() {
    const token = localStorage.getItem("token");

    return fetch("/api/users/me/avatar/", {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  resetPassword({ email }) {
    return fetch("/api/users/reset_password/", {
      method: "POST",
      headers: {
        ...this._headers,
      },
      body: JSON.stringify({ email }),
    }).then((res) => this.checkResponse(res));
  }

  getRecipes({
    page = 1,
    limit = 6,
    is_favorited = 0,
    is_in_shopping_cart = 0,
    author,
    tags,
  } = {}) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};
    const tagsString = tags
      ? tags
          .filter((tag) => tag.value)
          .map((tag) => `&tags=${tag.slug}`)
          .join("")
      : "";

    return fetch(
      `/api/recipes/?page=${page}&limit=${limit}${
        author ? `&author=${author}` : ""
      }${is_favorited ? `&is_favorited=${is_favorited}` : ""}${
        is_in_shopping_cart ? `&is_in_shopping_cart=${is_in_shopping_cart}` : ""
      }${tagsString}`,
      {
        method: "GET",
        headers: {
          ...this._headers,
          ...authorization,
        },
      }
    ).then((res) => this.checkResponse(res));
  }

  getRecipe({ recipe_id } = {}) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};

    return fetch(`/api/recipes/${recipe_id}/`, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  getRecipeCalculated({ recipe_id, servings } = {}) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};
    const servingsQuery = servings ? `?servings=${servings}` : "";

    return fetch(`/appapi/recipes/${recipe_id}${servingsQuery}`, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  rateRecipe({ recipe_id, rating }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${recipe_id}/rating/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({ rating }),
    }).then((res) => this.checkResponse(res));
  }

  deleteRecipeRating({ recipe_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${recipe_id}/rating/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getRecipeComments({ recipe_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};

    return fetch(`/api/recipes/${recipe_id}/comments/`, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  createRecipeComment({ recipe_id, text, parent_id = null }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${recipe_id}/comments/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({ text, parent_id }),
    }).then((res) => this.checkResponse(res));
  }

  patchComment({ comment_id, text }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/comments/${comment_id}/`, {
      method: "PATCH",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({ text }),
    }).then((res) => this.checkResponse(res));
  }

  deleteComment({ comment_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/comments/${comment_id}/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  createRecipe({
    name = "",
    image,
    tags = [],
    cooking_time = 0,
    text = "",
    ingredients = [],
  }) {
    const token = localStorage.getItem("token");

    return fetch("/api/recipes/", {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({
        name,
        image,
        tags,
        cooking_time,
        text,
        ingredients,
      }),
    }).then((res) => this.checkResponse(res));
  }

  updateRecipe(
    { name, recipe_id, image, tags, cooking_time, text, ingredients },
    wasImageUpdated
  ) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${recipe_id}/`, {
      method: "PATCH",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({
        name,
        id: recipe_id,
        image: wasImageUpdated ? image : undefined,
        tags,
        cooking_time: Number(cooking_time),
        text,
        ingredients,
      }),
    }).then((res) => this.checkResponse(res));
  }

  addToFavorites({ id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${id}/favorite/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  removeFromFavorites({ id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${id}/favorite/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  copyRecipeLink({ id }) {
    return fetch(`/api/recipes/${id}/get-link/`, {
      method: "GET",
      headers: {
        ...this._headers,
      },
    }).then((res) => this.checkResponse(res));
  }

  getUser({ id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};

    return fetch(`/api/users/${id}/`, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  getUsers({ page = 1, limit = 6 }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/users/?page=${page}&limit=${limit}`, {
      method: "GET",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getSubscriptions({ page, limit = 6, recipes_limit = 3 }) {
    const token = localStorage.getItem("token");

    return fetch(
      `/api/users/subscriptions/?page=${page}&limit=${limit}&recipes_limit=${recipes_limit}`,
      {
        method: "GET",
        headers: {
          ...this._headers,
          authorization: `Token ${token}`,
        },
      }
    ).then((res) => this.checkResponse(res));
  }

  deleteSubscriptions({ author_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/users/${author_id}/subscribe/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  subscribe({ author_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/users/${author_id}/subscribe/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getIngredients({ name }) {
    return fetch(`/api/ingredients/?name=${name}`, {
      method: "GET",
      headers: {
        ...this._headers,
      },
    }).then((res) => this.checkResponse(res));
  }

  getTags() {
    return fetch("/api/tags/", {
      method: "GET",
      headers: {
        ...this._headers,
      },
    }).then((res) => this.checkResponse(res));
  }

  addToOrders({ id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${id}/shopping_cart/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  removeFromOrders({ id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${id}/shopping_cart/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  deleteRecipe({ recipe_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/recipes/${recipe_id}/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  downloadFile() {
    const token = localStorage.getItem("token");

    return fetch("/api/recipes/download_shopping_cart/", {
      method: "GET",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkFileDownloadResponse(res));
  }

  likeComment({ comment_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/comments/${comment_id}/like/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  unlikeComment({ comment_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/api/comments/${comment_id}/like/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getCollections() {
    const token = localStorage.getItem("token");

    return fetch("/collections/", {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  createCollection({ name, description = "" }) {
    const token = localStorage.getItem("token");

    return fetch("/collections/", {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name,
        description: description || null,
      }),
    }).then((res) => this.checkResponse(res));
  }

  getCollection({ collection_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Bearer ${token}` } : {};

    return fetch(`/collections/${collection_id}/`, {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  updateCollection({ collection_id, name, description = "" }) {
    const token = localStorage.getItem("token");

    return fetch(`/collections/${collection_id}/`, {
      method: "PATCH",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        name,
        description: description || null,
      }),
    }).then((res) => this.checkResponse(res));
  }

  deleteCollection({ collection_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/collections/${collection_id}/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getCollectionRecipes({ collection_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Bearer ${token}` } : {};

    return fetch(`/collections/${collection_id}/recipes/`, {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then((res) => this.checkResponse(res));
  }

  addRecipeToCollection({ collection_id, recipe_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/collections/${collection_id}/recipes/${recipe_id}/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  removeRecipeFromCollection({ collection_id, recipe_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/collections/${collection_id}/recipes/${recipe_id}/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  getRecipeCollections({ recipe_id }) {
    const token = localStorage.getItem("token");

    return fetch(`/recipes/${recipe_id}/collections/`, {
      method: "GET",
      cache: "no-store",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
    }).then((res) => this.checkResponse(res));
  }

  updateRecipeCollections({ recipe_id, collection_ids = [] }) {
    const token = localStorage.getItem("token");

    return fetch(`/recipes/${recipe_id}/collections/`, {
      method: "PUT",
      headers: {
        ...this._headers,
        authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        collection_ids,
      }),
    }).then((res) => this.checkResponse(res));
  }
}

export default new Api(process.env.API_URL || "http://localhost", {
  "content-type": "application/json",
});