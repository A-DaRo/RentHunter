# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import numpy as np
from itemadapter import ItemAdapter

class FormatCSVPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Ensure all fields are strings for CSV export and replace None with NaN
        for field in adapter.field_names():
            value = adapter.get(field)
            if value is None:
                adapter[field] = np.nan
            else:
                adapter[field] = str(value)

        return item