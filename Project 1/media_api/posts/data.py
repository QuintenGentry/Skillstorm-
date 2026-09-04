"""
Used to populate the Post table with data. 
"""

from datetime import datetime

POSTS = [
    {"platform": "twitter", "caption_text": "We just discovered that customer records — including names like Jordan Miles and emails such as jmiles4821@examplemail.net — were exposed due to a security lapse. This kind of breach of personal information is unacceptable, and we're taking immediate action to address it.", "image": "image1.png", "scheduled_publish_time": datetime(2026, 9, 2, 15, 45), "compliance_status": "blocked", "brand_id": 1},
    {"platform": "instagram", "caption_text": "Thanks to our new security upgrades, sensitive details like Client ID #A92-4471 and contact email: sarah.chen@fakesecure.org are now protected with enhanced encryption. Your personal information has never been safer.", "image": "image2.png", "scheduled_publish_time": datetime(2026, 9, 4, 14, 0), "compliance_status": "blocked", "brand_id": 1},
    {"platform": "facebook", "caption_text": "Following a recent audit, we identified unauthorized exposure of limited client data. This is absolutely unacceptable, any personel who leaked this data will be fired immediately to ensure this never happens again.", "image": "image3.jpg", "scheduled_publish_time": datetime(2026, 8, 29, 6, 30), "compliance_status": "pending", "brand_id": 1},
    {"platform": "facebook", "caption_text":  "Our latest compliance update strengthens protection for sensitive identifiers. These enhancements reflect our continued commitment to safeguarding personal information across all operational systems.", "image": "image4.png", "scheduled_publish_time": datetime(2026, 8, 28, 14, 30), "compliance_status": "pending", "brand_id": 2},
    {"platform": "linkedin", "caption_text": "A recent internal review identified gaps in our data-handling procedures that do not meet our operational standards. We are implementing corrective measures immediately to strengthen oversight and prevent future disruptions.", "image": "image5.jpg", "scheduled_publish_time": datetime(2026, 8, 27, 18, 15), "compliance_status": "approved", "brand_id": 4},
    {"platform": "twitter", "caption_text": "Our latest system update enhances security, improves workflow efficiency, and reinforces our commitment to maintaining the highest standards across all operations. We appreciate the continued trust placed in our team.", "image": "image6.png", "scheduled_publish_time": datetime(2026, 8, 31, 19, 0), "compliance_status": "approved", "brand_id": 3}
]
