CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);

CREATE TABLE public.store_address (
    id bigint NOT NULL,
    locality character varying(150) NOT NULL,
    city character varying(150) NOT NULL,
    state character varying(150) NOT NULL,
    user_id integer NOT NULL
);

CREATE TABLE public.store_cart (
    id bigint NOT NULL,
    quantity integer NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    product_id bigint NOT NULL,
    user_id integer NOT NULL,
    CONSTRAINT store_cart_quantity_check CHECK ((quantity >= 0))
);


CREATE TABLE public.store_order (
    id bigint NOT NULL,
    quantity integer NOT NULL,
    ordered_date timestamp with time zone NOT NULL,
    status character varying(50) NOT NULL,
    address_id bigint NOT NULL,
    product_id bigint NOT NULL,
    user_id integer NOT NULL,
    CONSTRAINT store_order_quantity_check CHECK ((quantity >= 0))
);

CREATE TABLE public.store_product (
    id bigint NOT NULL,
    title character varying(150) NOT NULL,
    slug character varying(160) NOT NULL,
    short_description text NOT NULL,
    detail_description text,
    product_image character varying(100),
    price numeric(8,2) NOT NULL,
    is_active boolean NOT NULL,
    is_featured boolean NOT NULL,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL,
    category_id bigint NOT NULL,
    sku character varying(255) NOT NULL
);


----------------------------------------------------------------------------
 TRUNCATE auth_user;
 TRUNCATE store_address;
 TRUNCATE store_cart;
 TRUNCATE store_order;
 TRUNCATE store_product;