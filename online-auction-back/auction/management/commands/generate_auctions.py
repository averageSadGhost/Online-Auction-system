import random
import requests
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

from auction.models import Auction


# Auction item templates organized by category
AUCTION_ITEMS = {
    "electronics": [
        {
            "title": "Sony Walkman TPS-L2",
            "description": "Original 1979 Sony Walkman TPS-L2 in excellent working condition. The first portable cassette player that revolutionized how people listen to music. Includes original headphones MDR-3L2 and leather carrying case. Battery compartment clean, plays tapes smoothly.",
            "image_query": "sony walkman vintage cassette player",
            "price_range": (200, 600)
        },
        {
            "title": "Apple Macintosh 128K Computer",
            "description": "The original Apple Macintosh 128K from 1984. This iconic beige computer changed personal computing forever with its revolutionary graphical user interface. Fully functional with original keyboard, mouse, and system disks. A must-have for any Apple collector.",
            "image_query": "apple macintosh 128k vintage computer",
            "price_range": (1500, 5000)
        },
        {
            "title": "Canon EOS 5D Mark IV DSLR",
            "description": "Professional-grade Canon EOS 5D Mark IV with 30.4 megapixel full-frame sensor. Includes 24-70mm f/2.8L lens, 70-200mm f/2.8L lens, Speedlite 600EX flash, and professional carrying case. Low shutter count, mint condition.",
            "image_query": "canon eos 5d camera dslr professional",
            "price_range": (2000, 4500)
        },
        {
            "title": "McIntosh MC275 Tube Amplifier",
            "description": "Legendary McIntosh MC275 vacuum tube power amplifier. 75 watts per channel of pure audiophile bliss. Recently serviced with new tubes. The warm, rich sound that solid-state amplifiers simply cannot replicate. Includes original box and manual.",
            "image_query": "mcintosh tube amplifier vintage audio",
            "price_range": (3000, 6000)
        },
        {
            "title": "Nintendo Game Boy Original",
            "description": "Original 1989 Nintendo Game Boy DMG-01 in working condition. The handheld that defined portable gaming. Includes Tetris cartridge, carrying case, and link cable. Screen has no dead pixels, sound works perfectly.",
            "image_query": "nintendo game boy original handheld",
            "price_range": (100, 300)
        },
        {
            "title": "Polaroid SX-70 Land Camera",
            "description": "Iconic Polaroid SX-70 folding instant camera in chrome and tan leather. The first SLR instant camera ever made. Recently serviced, takes perfect instant photos. A piece of photographic history.",
            "image_query": "polaroid sx-70 instant camera vintage",
            "price_range": (250, 500)
        },
        {
            "title": "Bang & Olufsen Beogram 4000",
            "description": "Stunning Bang & Olufsen Beogram 4000 turntable with tangential tonearm. Danish design excellence from 1972. Fully restored with new belt and stylus. Plays records with incredible precision and style.",
            "image_query": "bang olufsen turntable beogram vinyl",
            "price_range": (800, 1800)
        },
    ],
    "jewelry": [
        {
            "title": "Art Deco Diamond Engagement Ring",
            "description": "Breathtaking Art Deco diamond ring from the 1920s. Features a 2.1 carat old European cut center diamond (G color, VS1 clarity) surrounded by French-cut sapphires in a platinum filigree setting. Certified by GIA.",
            "image_query": "art deco diamond ring platinum vintage",
            "price_range": (8000, 25000)
        },
        {
            "title": "Mikimoto Akoya Pearl Necklace",
            "description": "Exquisite Mikimoto Akoya pearl necklace featuring 55 perfectly matched 8mm pearls. AAA quality with exceptional luster and rose overtones. 18k white gold clasp with diamond accent. Original Mikimoto box and certificate.",
            "image_query": "mikimoto pearl necklace luxury jewelry",
            "price_range": (3000, 8000)
        },
        {
            "title": "Cartier Love Bracelet 18K Gold",
            "description": "Authentic Cartier Love bracelet in 18k yellow gold. Size 17. The iconic design with screw motifs that has symbolized love since 1969. Includes original screwdriver, box, and certificate. Excellent condition.",
            "image_query": "cartier love bracelet gold luxury",
            "price_range": (5000, 8000)
        },
        {
            "title": "Colombian Emerald Pendant",
            "description": "Stunning 4.5 carat Colombian emerald pendant in 18k white gold setting. Vivid green color with excellent transparency. Surrounded by 1.2 carats of brilliant cut diamonds. Comes with gemological certificate.",
            "image_query": "emerald pendant necklace diamond gold",
            "price_range": (6000, 15000)
        },
        {
            "title": "Tiffany & Co. Diamond Tennis Bracelet",
            "description": "Classic Tiffany & Co. diamond tennis bracelet in platinum. Features 40 round brilliant diamonds totaling 5.0 carats (F-G color, VS clarity). Timeless elegance with original Tiffany blue box.",
            "image_query": "tiffany diamond tennis bracelet platinum",
            "price_range": (10000, 20000)
        },
        {
            "title": "Van Cleef & Arpels Alhambra Necklace",
            "description": "Iconic Van Cleef & Arpels Vintage Alhambra necklace in 18k yellow gold with mother of pearl motifs. 10 motif design. The lucky clover design that has been a symbol of elegance since 1968. Complete set with box and papers.",
            "image_query": "van cleef arpels alhambra necklace gold",
            "price_range": (8000, 15000)
        },
        {
            "title": "Sapphire and Diamond Earrings",
            "description": "Magnificent pair of Ceylon sapphire drop earrings. Each earring features a 3 carat oval blue sapphire surrounded by brilliant diamonds, set in 18k white gold. Total diamond weight 2.0 carats. Stunning royal blue color.",
            "image_query": "sapphire diamond earrings blue gold",
            "price_range": (7000, 18000)
        },
    ],
    "watches": [
        {
            "title": "Rolex Submariner Date 116610LN",
            "description": "Rolex Submariner Date reference 116610LN in stainless steel. Black ceramic bezel, black dial. 40mm case with Oyster bracelet. Complete set with box, papers, and warranty card dated 2019. Excellent condition with minimal wear.",
            "image_query": "rolex submariner black watch luxury",
            "price_range": (10000, 15000)
        },
        {
            "title": "Omega Speedmaster Professional Moonwatch",
            "description": "Omega Speedmaster Professional 'Moonwatch' reference 311.30.42.30.01.005. The same watch worn on the moon. Manual-winding caliber 1861. 42mm stainless steel case. Full set with box, papers, and NASA strap.",
            "image_query": "omega speedmaster moonwatch chronograph",
            "price_range": (5000, 8000)
        },
        {
            "title": "Patek Philippe Calatrava 5196G",
            "description": "Elegant Patek Philippe Calatrava reference 5196G in 18k white gold. Silver opaline dial with gold applied hour markers. 37mm case, manual-winding caliber 215 PS. The quintessential dress watch. Box and extract from archives.",
            "image_query": "patek philippe calatrava dress watch gold",
            "price_range": (20000, 35000)
        },
        {
            "title": "Audemars Piguet Royal Oak 15400ST",
            "description": "Audemars Piguet Royal Oak 'Jumbo' reference 15400ST in stainless steel. Blue 'Grande Tapisserie' dial. 41mm case designed by Gerald Genta. Self-winding caliber 3120. Complete with box and papers.",
            "image_query": "audemars piguet royal oak blue steel",
            "price_range": (25000, 40000)
        },
        {
            "title": "Cartier Tank Francaise Large",
            "description": "Cartier Tank Francaise in 18k yellow gold. Large size with silver dial, Roman numerals, and blue steel hands. Automatic movement. The iconic rectangular design that has defined elegance since 1917. Full set.",
            "image_query": "cartier tank francaise gold watch",
            "price_range": (8000, 15000)
        },
        {
            "title": "IWC Portugieser Chronograph",
            "description": "IWC Portugieser Chronograph reference IW371446 in stainless steel. Silver dial with blue hands and Arabic numerals. 40.9mm case with stunning domed sapphire crystal. One of the most beautiful chronographs ever made.",
            "image_query": "iwc portugieser chronograph silver dial",
            "price_range": (6000, 10000)
        },
        {
            "title": "Tudor Black Bay Fifty-Eight",
            "description": "Tudor Black Bay Fifty-Eight reference 79030N in stainless steel. Black dial and bezel, 39mm case perfect for smaller wrists. In-house MT5402 movement. The vintage-inspired diver that took the watch world by storm.",
            "image_query": "tudor black bay fifty eight diver watch",
            "price_range": (3000, 4500)
        },
    ],
    "vehicles": [
        {
            "title": "1967 Ford Mustang Shelby GT500",
            "description": "Legendary 1967 Ford Mustang Shelby GT500 in Wimbledon White with blue Le Mans stripes. Numbers-matching 428 Police Interceptor V8 engine producing 355 horsepower. 4-speed manual transmission. Frame-off restoration with documentation. Shelby Registry certified.",
            "image_query": "1967 ford mustang shelby gt500 white classic",
            "price_range": (120000, 200000)
        },
        {
            "title": "1973 Porsche 911 Carrera RS",
            "description": "Iconic 1973 Porsche 911 Carrera RS 2.7 in Grand Prix White with green script. One of only 1,580 produced. Matching numbers with original engine. Documented history from new. The lightweight homologation special that defined Porsche performance.",
            "image_query": "porsche 911 carrera rs white classic",
            "price_range": (500000, 800000)
        },
        {
            "title": "1969 Chevrolet Camaro Z/28",
            "description": "Stunning 1969 Chevrolet Camaro Z/28 in Hugger Orange. Original DZ 302 small-block V8 with solid lifter cam. 4-speed Muncie transmission, 12-bolt rear end. Cowl induction hood, rally wheels. Rotisserie restoration.",
            "image_query": "1969 chevrolet camaro z28 orange muscle car",
            "price_range": (80000, 130000)
        },
        {
            "title": "1965 Aston Martin DB5",
            "description": "The James Bond car - 1965 Aston Martin DB5 in Silver Birch. 4.0L inline-six engine with triple SU carburetors. 5-speed ZF manual gearbox. Fully restored to concours condition. One of the most desirable British sports cars ever made.",
            "image_query": "aston martin db5 silver classic james bond",
            "price_range": (700000, 1200000)
        },
        {
            "title": "1970 Dodge Challenger R/T Hemi",
            "description": "Numbers-matching 1970 Dodge Challenger R/T with 426 Hemi V8. Plum Crazy Purple with white vinyl top. Pistol grip 4-speed transmission. Only 356 Hemi Challengers built in 1970. Investment-grade muscle car.",
            "image_query": "1970 dodge challenger rt hemi purple muscle",
            "price_range": (150000, 250000)
        },
        {
            "title": "1961 Ferrari 250 GT SWB",
            "description": "Breathtaking 1961 Ferrari 250 GT SWB Berlinetta in Rosso Corsa. Colombo V12 engine, 4-speed manual with outside gate shifter. Disc brakes all around. Ferrari Classiche certified. One of Enzo's masterpieces.",
            "image_query": "ferrari 250 gt swb red classic italian",
            "price_range": (8000000, 12000000)
        },
        {
            "title": "1957 Mercedes-Benz 300SL Roadster",
            "description": "Magnificent 1957 Mercedes-Benz 300SL Roadster in Midnight Blue. Bosch mechanical fuel injection, 3.0L inline-six. Both soft top and hardtop included. Matching numbers, tools, and fitted luggage. The sports car of the decade.",
            "image_query": "mercedes 300sl roadster blue classic convertible",
            "price_range": (1200000, 1800000)
        },
    ],
}


class Command(BaseCommand):
    help = 'Generate auction items with matched images from specific categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--category',
            type=str,
            choices=['electronics', 'jewelry', 'watches', 'vehicles', 'all'],
            default='all',
            help='Category of items to generate (default: all)'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of auctions per category (default: 5)'
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Maximum days ahead for auction start time (default: 7)'
        )
        parser.add_argument(
            '--duration-hours',
            type=int,
            default=24,
            help='Auction duration in hours (default: 24)'
        )

    def handle(self, *args, **options):
        category = options['category']
        count = options['count']
        days_ahead = options['days_ahead']
        duration_hours = options['duration_hours']

        # Determine which categories to process
        if category == 'all':
            categories = list(AUCTION_ITEMS.keys())
        else:
            categories = [category]

        total_created = 0

        for cat in categories:
            self.stdout.write(f'\nGenerating {count} {cat} auctions...')
            items = AUCTION_ITEMS[cat]

            # Select items (repeat if count > available items)
            selected_items = []
            while len(selected_items) < count:
                remaining = count - len(selected_items)
                selected_items.extend(random.sample(items, min(remaining, len(items))))

            for item in selected_items[:count]:
                # Generate unique title
                title = item['title']
                if Auction.objects.filter(title=title).exists():
                    title = f"{item['title']} #{random.randint(100, 999)}"

                # Calculate random start and end times
                start_offset = timedelta(
                    days=random.randint(0, days_ahead),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                start_time = timezone.now() + start_offset
                end_time = start_time + timedelta(hours=duration_hours)

                # Generate random price within the item's price range
                min_price, max_price = item['price_range']
                starting_price = Decimal(random.randint(min_price, max_price))

                # Download image using specific query
                image_content = self.download_image(item['image_query'])

                if not image_content:
                    self.stdout.write(
                        self.style.WARNING(f'  Skipping "{title}" - could not download image')
                    )
                    continue

                # Create the auction
                auction = Auction(
                    title=title,
                    description=item['description'],
                    start_date_time=start_time,
                    end_date_time=end_time,
                    starting_price=starting_price,
                    status='scheduled'
                )

                # Save the image
                safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in title)
                filename = f"{safe_title.lower().replace(' ', '_')[:50]}_{random.randint(1000, 9999)}.jpg"
                auction.image.save(filename, ContentFile(image_content), save=False)

                auction.save()
                total_created += 1

                self.stdout.write(
                    self.style.SUCCESS(f'  Created: {title} (${starting_price:,.0f})')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {total_created} auctions!')
        )

    def download_image(self, query):
        """Download an image from Unsplash based on search query."""
        # Use Unsplash Source API with specific search terms
        search_terms = query.replace(' ', ',')
        url = f"https://source.unsplash.com/800x600/?{search_terms}"

        try:
            response = requests.get(url, timeout=20, allow_redirects=True)
            if response.status_code == 200 and len(response.content) > 1000:
                return response.content
        except requests.RequestException as e:
            self.stdout.write(
                self.style.WARNING(f'  Unsplash error: {e}')
            )

        # Fallback to Lorem Picsum
        try:
            picsum_url = "https://picsum.photos/800/600"
            response = requests.get(picsum_url, timeout=15, allow_redirects=True)
            if response.status_code == 200:
                return response.content
        except requests.RequestException:
            pass

        return None
