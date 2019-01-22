#!/bin/bash
# Get the list of sites having a specific plugin active
# usage bash get_sites_using_plugin.sh

env=prod
#plugin=lemon-way-for-ecommerce/woocommerce-gateway-lemonway.php
plugin=ti-woocommerce-wishlist.php
db_prefix=Qd1wq5VS_


# get options tables (one for each sites)
tables=$( sudo -u www-data WP_ENV=$env /PJPO_WORDPRESS/vendor/bin/wp --path=/PJPO_WORDPRESS/web/wp db query "SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_NAME LIKE '$db_prefix%_options';" | sed 1d)
rescount=0

# if plugin is active, display the domain
for table in $tables
do
  # list of active plugins are in the row (option) active_plugins
  is_plugin_active=$( sudo -u www-data WP_ENV=$env /PJPO_WORDPRESS/vendor/bin/wp --path=/PJPO_WORDPRESS/web/wp db query "SELECT 1 FROM $table WHERE option_name='active_plugins' AND option_value LIKE '%$plugin%';" | sed 1d)
  if [[ $is_plugin_active -eq 1 ]]; then
    blog_table=$db_prefix'blogs'
    domain=$( sudo -u www-data WP_ENV=$env /PJPO_WORDPRESS/vendor/bin/wp --path=/PJPO_WORDPRESS/web/wp db query "SELECT domain from $blog_table where blog_id = SUBSTRING_INDEX(SUBSTRING_INDEX('$table', '_', 2), '_', -1)" | sed 1d)
    rescount=$((rescount + 1))
    client_id=$( sudo -u www-data WP_ENV=$env /PJPO_WORDPRESS/vendor/bin/wp --path=/PJPO_WORDPRESS/web/wp db query "SELECT option_value FROM $table WHERE option_name='_pj_customer_data';" | sed 1d | grep -oP '[id_client]*"(\d{8})"' | head -1 )
    echo "$domain"
    echo "$client_id"
  fi
done

echo "Sites using $plugin: $rescount"
