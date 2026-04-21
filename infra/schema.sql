--
-- PostgreSQL database dump
--

\restrict FySSgZyolqxTwhydzIsUcS1aZ4UtrKDdKpd9RuiDWdUrLVzxWVZxNUNjQNeHees

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO recipes_user;

--
-- Name: comment_likes; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.comment_likes (
    id integer NOT NULL,
    comment_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.comment_likes OWNER TO recipes_user;

--
-- Name: comment_likes_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.comment_likes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comment_likes_id_seq OWNER TO recipes_user;

--
-- Name: comment_likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.comment_likes_id_seq OWNED BY public.comment_likes.id;


--
-- Name: comments; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    author_id integer NOT NULL,
    text text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    parent_id integer
);


ALTER TABLE public.comments OWNER TO recipes_user;

--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comments_id_seq OWNER TO recipes_user;

--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: favorites; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.favorites (
    id integer NOT NULL,
    user_id integer NOT NULL,
    recipe_id integer NOT NULL
);


ALTER TABLE public.favorites OWNER TO recipes_user;

--
-- Name: favorites_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.favorites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.favorites_id_seq OWNER TO recipes_user;

--
-- Name: favorites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.favorites_id_seq OWNED BY public.favorites.id;


--
-- Name: ingredients; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.ingredients (
    id integer NOT NULL,
    name character varying(120) NOT NULL,
    unit character varying(32) NOT NULL
);


ALTER TABLE public.ingredients OWNER TO recipes_user;

--
-- Name: ingredients_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.ingredients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.ingredients_id_seq OWNER TO recipes_user;

--
-- Name: ingredients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.ingredients_id_seq OWNED BY public.ingredients.id;


--
-- Name: recipe_ingredients; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.recipe_ingredients (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    ingredient_id integer NOT NULL,
    amount numeric(10,2) NOT NULL
);


ALTER TABLE public.recipe_ingredients OWNER TO recipes_user;

--
-- Name: recipe_ingredients_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.recipe_ingredients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipe_ingredients_id_seq OWNER TO recipes_user;

--
-- Name: recipe_ingredients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.recipe_ingredients_id_seq OWNED BY public.recipe_ingredients.id;


--
-- Name: recipe_ratings; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.recipe_ratings (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    user_id integer NOT NULL,
    rating integer NOT NULL,
    CONSTRAINT ck_recipe_ratings_rating_range CHECK (((rating >= 1) AND (rating <= 5)))
);


ALTER TABLE public.recipe_ratings OWNER TO recipes_user;

--
-- Name: recipe_ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.recipe_ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipe_ratings_id_seq OWNER TO recipes_user;

--
-- Name: recipe_ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.recipe_ratings_id_seq OWNED BY public.recipe_ratings.id;


--
-- Name: recipe_steps; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.recipe_steps (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    "position" integer NOT NULL,
    text text NOT NULL,
    duration_sec integer
);


ALTER TABLE public.recipe_steps OWNER TO recipes_user;

--
-- Name: recipe_steps_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.recipe_steps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipe_steps_id_seq OWNER TO recipes_user;

--
-- Name: recipe_steps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.recipe_steps_id_seq OWNED BY public.recipe_steps.id;


--
-- Name: recipe_tags; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.recipe_tags (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.recipe_tags OWNER TO recipes_user;

--
-- Name: recipe_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.recipe_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipe_tags_id_seq OWNER TO recipes_user;

--
-- Name: recipe_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.recipe_tags_id_seq OWNED BY public.recipe_tags.id;


--
-- Name: recipes; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.recipes (
    id integer NOT NULL,
    title character varying(120) NOT NULL,
    description text NOT NULL,
    cooking_time_minutes integer NOT NULL,
    author_id integer NOT NULL,
    image text
);


ALTER TABLE public.recipes OWNER TO recipes_user;

--
-- Name: recipes_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.recipes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recipes_id_seq OWNER TO recipes_user;

--
-- Name: recipes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.recipes_id_seq OWNED BY public.recipes.id;


--
-- Name: shopping_cart; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.shopping_cart (
    id integer NOT NULL,
    user_id integer NOT NULL,
    recipe_id integer NOT NULL
);


ALTER TABLE public.shopping_cart OWNER TO recipes_user;

--
-- Name: shopping_cart_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.shopping_cart_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shopping_cart_id_seq OWNER TO recipes_user;

--
-- Name: shopping_cart_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.shopping_cart_id_seq OWNED BY public.shopping_cart.id;


--
-- Name: short_links; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.short_links (
    id integer NOT NULL,
    recipe_id integer NOT NULL,
    code character varying(16) NOT NULL
);


ALTER TABLE public.short_links OWNER TO recipes_user;

--
-- Name: short_links_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.short_links_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.short_links_id_seq OWNER TO recipes_user;

--
-- Name: short_links_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.short_links_id_seq OWNED BY public.short_links.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    author_id integer NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO recipes_user;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO recipes_user;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: tags; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.tags (
    id integer NOT NULL,
    name character varying(60) NOT NULL,
    slug character varying(60) NOT NULL,
    color character varying(7) NOT NULL
);


ALTER TABLE public.tags OWNER TO recipes_user;

--
-- Name: tags_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tags_id_seq OWNER TO recipes_user;

--
-- Name: tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.tags_id_seq OWNED BY public.tags.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: recipes_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(60) NOT NULL,
    password_hash character varying(255) NOT NULL,
    is_admin boolean DEFAULT false NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    avatar text
);


ALTER TABLE public.users OWNER TO recipes_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: recipes_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO recipes_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: recipes_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: comment_likes id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comment_likes ALTER COLUMN id SET DEFAULT nextval('public.comment_likes_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: favorites id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.favorites ALTER COLUMN id SET DEFAULT nextval('public.favorites_id_seq'::regclass);


--
-- Name: ingredients id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.ingredients ALTER COLUMN id SET DEFAULT nextval('public.ingredients_id_seq'::regclass);


--
-- Name: recipe_ingredients id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ingredients ALTER COLUMN id SET DEFAULT nextval('public.recipe_ingredients_id_seq'::regclass);


--
-- Name: recipe_ratings id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ratings ALTER COLUMN id SET DEFAULT nextval('public.recipe_ratings_id_seq'::regclass);


--
-- Name: recipe_steps id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_steps ALTER COLUMN id SET DEFAULT nextval('public.recipe_steps_id_seq'::regclass);


--
-- Name: recipe_tags id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_tags ALTER COLUMN id SET DEFAULT nextval('public.recipe_tags_id_seq'::regclass);


--
-- Name: recipes id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipes ALTER COLUMN id SET DEFAULT nextval('public.recipes_id_seq'::regclass);


--
-- Name: shopping_cart id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.shopping_cart ALTER COLUMN id SET DEFAULT nextval('public.shopping_cart_id_seq'::regclass);


--
-- Name: short_links id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.short_links ALTER COLUMN id SET DEFAULT nextval('public.short_links_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.tags ALTER COLUMN id SET DEFAULT nextval('public.tags_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: comment_likes comment_likes_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comment_likes
    ADD CONSTRAINT comment_likes_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: favorites favorites_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_pkey PRIMARY KEY (id);


--
-- Name: ingredients ingredients_name_key; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_name_key UNIQUE (name);


--
-- Name: ingredients ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.ingredients
    ADD CONSTRAINT ingredients_pkey PRIMARY KEY (id);


--
-- Name: recipe_ingredients recipe_ingredients_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_pkey PRIMARY KEY (id);


--
-- Name: recipe_ratings recipe_ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ratings
    ADD CONSTRAINT recipe_ratings_pkey PRIMARY KEY (id);


--
-- Name: recipe_steps recipe_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_steps
    ADD CONSTRAINT recipe_steps_pkey PRIMARY KEY (id);


--
-- Name: recipe_tags recipe_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_pkey PRIMARY KEY (id);


--
-- Name: recipes recipes_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (id);


--
-- Name: shopping_cart shopping_cart_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.shopping_cart
    ADD CONSTRAINT shopping_cart_pkey PRIMARY KEY (id);


--
-- Name: short_links short_links_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.short_links
    ADD CONSTRAINT short_links_pkey PRIMARY KEY (id);


--
-- Name: short_links short_links_recipe_id_key; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.short_links
    ADD CONSTRAINT short_links_recipe_id_key UNIQUE (recipe_id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: tags tags_name_key; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_name_key UNIQUE (name);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: tags tags_slug_key; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_slug_key UNIQUE (slug);


--
-- Name: comment_likes uq_comment_likes_comment_user; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comment_likes
    ADD CONSTRAINT uq_comment_likes_comment_user UNIQUE (comment_id, user_id);


--
-- Name: favorites uq_favorites_user_recipe; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT uq_favorites_user_recipe UNIQUE (user_id, recipe_id);


--
-- Name: recipe_ingredients uq_recipe_ingredient; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT uq_recipe_ingredient UNIQUE (recipe_id, ingredient_id);


--
-- Name: recipe_ratings uq_recipe_ratings_recipe_user; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ratings
    ADD CONSTRAINT uq_recipe_ratings_recipe_user UNIQUE (recipe_id, user_id);


--
-- Name: recipe_steps uq_recipe_steps_recipe_id_position; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_steps
    ADD CONSTRAINT uq_recipe_steps_recipe_id_position UNIQUE (recipe_id, "position");


--
-- Name: recipe_tags uq_recipe_tag; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT uq_recipe_tag UNIQUE (recipe_id, tag_id);


--
-- Name: shopping_cart uq_shopping_cart_user_recipe; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.shopping_cart
    ADD CONSTRAINT uq_shopping_cart_user_recipe UNIQUE (user_id, recipe_id);


--
-- Name: short_links uq_short_links_code; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.short_links
    ADD CONSTRAINT uq_short_links_code UNIQUE (code);


--
-- Name: subscriptions uq_subscriptions_user_author; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT uq_subscriptions_user_author UNIQUE (user_id, author_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: ix_comment_likes_comment_id; Type: INDEX; Schema: public; Owner: recipes_user
--

CREATE INDEX ix_comment_likes_comment_id ON public.comment_likes USING btree (comment_id);


--
-- Name: ix_comment_likes_user_id; Type: INDEX; Schema: public; Owner: recipes_user
--

CREATE INDEX ix_comment_likes_user_id ON public.comment_likes USING btree (user_id);


--
-- Name: ix_comments_author_id; Type: INDEX; Schema: public; Owner: recipes_user
--

CREATE INDEX ix_comments_author_id ON public.comments USING btree (author_id);


--
-- Name: ix_comments_parent_id; Type: INDEX; Schema: public; Owner: recipes_user
--

CREATE INDEX ix_comments_parent_id ON public.comments USING btree (parent_id);


--
-- Name: ix_comments_recipe_id; Type: INDEX; Schema: public; Owner: recipes_user
--

CREATE INDEX ix_comments_recipe_id ON public.comments USING btree (recipe_id);


--
-- Name: ix_recipe_steps_recipe_id; Type: INDEX; Schema: public; Owner: recipes_user
--

CREATE INDEX ix_recipe_steps_recipe_id ON public.recipe_steps USING btree (recipe_id);


--
-- Name: comment_likes comment_likes_comment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comment_likes
    ADD CONSTRAINT comment_likes_comment_id_fkey FOREIGN KEY (comment_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: comment_likes comment_likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comment_likes
    ADD CONSTRAINT comment_likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: comments comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: comments comments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: comments comments_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: favorites favorites_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.favorites
    ADD CONSTRAINT favorites_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recipes fk_recipes_author_id_users; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipes
    ADD CONSTRAINT fk_recipes_author_id_users FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recipe_ingredients recipe_ingredients_ingredient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_ingredient_id_fkey FOREIGN KEY (ingredient_id) REFERENCES public.ingredients(id) ON DELETE CASCADE;


--
-- Name: recipe_ingredients recipe_ingredients_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ingredients
    ADD CONSTRAINT recipe_ingredients_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_ratings recipe_ratings_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ratings
    ADD CONSTRAINT recipe_ratings_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_ratings recipe_ratings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_ratings
    ADD CONSTRAINT recipe_ratings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: recipe_steps recipe_steps_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_steps
    ADD CONSTRAINT recipe_steps_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_tags recipe_tags_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: recipe_tags recipe_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.recipe_tags
    ADD CONSTRAINT recipe_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: shopping_cart shopping_cart_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.shopping_cart
    ADD CONSTRAINT shopping_cart_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: shopping_cart shopping_cart_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.shopping_cart
    ADD CONSTRAINT shopping_cart_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: short_links short_links_recipe_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.short_links
    ADD CONSTRAINT short_links_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES public.recipes(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: recipes_user
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict FySSgZyolqxTwhydzIsUcS1aZ4UtrKDdKpd9RuiDWdUrLVzxWVZxNUNjQNeHees

