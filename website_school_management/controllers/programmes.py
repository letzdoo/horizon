import logging

from odoo import http
from odoo.http import Response, request

from odoo.addons.http_routing.models.ir_http import slug, unslug

_logger = logging.getLogger(__name__)


# Gestion des différentes routes pour les programmes de cours
class programmes(http.Controller):
    # Génération du breadcrumb
    def _get_breadcrumb(self, program, segment):
        breadcrumb = [{"uri": "/programmes/", "name": "Tous les programmes"}]
        if segment >= 1 and program.year_name:
            breadcrumb.append(
                {"uri": "/programmes/" + program.year_name, "name": program.year_name}
            )
            if segment >= 2 and program.domain_name:
                breadcrumb.append(
                    {
                        "uri": "/programmes/"
                        + program.year_name
                        + "/"
                        + program.domain_slug,
                        "name": program.domain_name,
                    }
                )
                if segment >= 3 and program.track_name:
                    breadcrumb.append(
                        {
                            "uri": "/programmes/"
                            + program.year_name
                            + "/"
                            + program.domain_slug
                            + "/"
                            + program.track_slug,
                            "name": program.track_name,
                        }
                    )
                    if segment >= 4 and program.speciality_name:
                        breadcrumb.append(
                            {
                                "uri": "/programmes/"
                                + program.year_name
                                + "/"
                                + program.domain_slug
                                + "/"
                                + program.track_slug
                                + "/"
                                + program.speciality_slug,
                                "name": program.speciality_name,
                            }
                        )
                        if segment >= 5 and program.cycle_grade:
                            breadcrumb.append(
                                {
                                    "uri": "/programmes/"
                                    + program.year_name
                                    + "/"
                                    + program.domain_slug
                                    + "/"
                                    + program.track_slug
                                    + "/"
                                    + program.speciality_slug
                                    + "/"
                                    + program.cycle_grade_slug,
                                    "name": program.cycle_grade,
                                },
                            )
                            if segment >= 6 and program.cycle_subtype:
                                breadcrumb.append(
                                    {
                                        "uri": "/programmes/"
                                        + program.year_name
                                        + "/"
                                        + program.domain_slug
                                        + "/"
                                        + program.track_slug
                                        + "/"
                                        + program.speciality_slug
                                        + "/"
                                        + program.cycle_grade_slug
                                        + "/"
                                        + program.cycle_subtype_slug,
                                        "name": program.cycle_subtype,
                                    }
                                )
                                if segment >= 7 and program.specialization:
                                    breadcrumb.append(
                                        {
                                            "uri": "/programme/" + slug(program),
                                            "name": program.specialization,
                                        }
                                    )
        return breadcrumb

    # Génération des options
    def _get_options(self, programs, segment):  # noqa: C901
        actual = request.httprequest.path
        options = []
        if segment == 0:
            for program in programs:
                option = {
                    "uri": actual + "/" + program.year_name,
                    "name": program.year_name,
                }
                if option not in options:
                    options.append(option)
        if segment == 1:
            for program in programs:
                option = {
                    "uri": actual + "/" + program.domain_slug,
                    "name": program.domain_name,
                }
                if option not in options:
                    options.append(option)
        elif segment == 2:
            for program in programs:
                option = {
                    "uri": actual + "/" + program.track_slug,
                    "name": program.track_name,
                }
                if option not in options:
                    options.append(option)
        elif segment == 3:
            for program in programs:
                option = {
                    "uri": actual + "/" + program.speciality_slug,
                    "name": program.speciality_name,
                }
                if option not in options:
                    options.append(option)
        elif segment == 4:
            for program in programs:
                option = {
                    "uri": actual + "/" + program.cycle_grade_slug,
                    "name": program.cycle_grade,
                }
                if option not in options:
                    options.append(option)
        elif segment == 5:
            for program in programs:
                if program.cycle_subtype_slug and program.cycle_subtype:
                    option = {
                        "uri": actual + "/" + program.cycle_subtype_slug,
                        "name": program.cycle_subtype,
                    }
                else:
                    option = "-"
                if option not in options:
                    options.append(option)
        elif segment == 6:
            for program in programs:
                if program.specialization_slug and program.specialization:
                    option = {
                        "uri": actual + "/" + program.specialization_slug,
                        "name": program.specialization,
                    }
                else:
                    option = "-"
                if option not in options:
                    options.append(option)
        return options

    # Génération de la sitemap
    def _sitemap_programs(env, rule, qs):  # noqa: disable=B902
        searchParams = [
            ("state", "=", "published"),
            ("domain_name", "!=", None),
            ("track_name", "!=", None),
        ]
        programs = env["school.program"].search(searchParams)

        breadcrumb = set()

        for prog in programs:
            loc = "/programme/%s" % slug(prog)
            if not qs or qs.lower() in loc:
                yield {"loc": loc}

            if prog.year_name:
                url = "/programmes/" + prog.year_name
                breadcrumb.add(url)
                if prog.domain_slug:
                    url = url + "/" + prog.domain_slug
                    breadcrumb.add(url)
                    if prog.track_slug:
                        url = url + "/" + prog.track_slug
                        breadcrumb.add(url)
                        if prog.speciality_slug:
                            url = url + "/" + prog.speciality_slug
                            breadcrumb.add(url)
                            if prog.cycle_grade_slug:
                                url = url + "/" + prog.cycle_grade_slug
                                breadcrumb.add(url)
                                if prog.cycle_subtype_slug:
                                    url = url + "/" + prog.cycle_subtype_slug
                                    breadcrumb.add(url)
                                    if prog.specialization_slug:
                                        url = url + "/" + prog.specialization_slug
                                        breadcrumb.add(url)

        for url in breadcrumb:
            if not qs or qs.lower() in url:
                yield {"loc": url, "priority": 0.4}

    @http.route(
        [
            "/programmes",
            "/programmes/<string:year>",
            "/programmes/<string:year>/<string:domain>",
            "/programmes/<string:year>/<string:domain>/<string:track>",
            "/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>",
            "/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>/<string:cycle_type>",
            "/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>/<string:cycle_type>/<string:cycle_subtype>",
            "/programmes/<string:year>/<string:domain>/<string:track>/<string:speciality>/<string:cycle_type>/<string:cycle_subtype>/<string:specialization>",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def programmes(
        self,
        year=None,
        domain=None,
        track=None,
        speciality=None,
        cycle_type=None,
        cycle_subtype=None,
        specialization=None,
        **post
    ):
        # Préparation des paramètres de recherche
        searchParams = [
            ("state", "=", "published"),
            ("domain_name", "!=", None),
            ("track_name", "!=", None),
        ]
        segment = 0
        if year:
            searchParams.append(("year_name", "=", year))
            segment = 1
            if domain:
                searchParams.append(("domain_slug", "=", domain))
                segment = 2
                if track:
                    searchParams.append(("track_slug", "=", track))
                    segment = 3
                    if speciality:
                        searchParams.append(("speciality_slug", "=", speciality))
                        segment = 4
                        if cycle_type:
                            searchParams.append(("cycle_grade_slug", "=", cycle_type))
                            segment = 5
                            if cycle_subtype:
                                searchParams.append(
                                    ("cycle_subtype_slug", "=", cycle_subtype)
                                )
                                segment = 6
                                if specialization:
                                    searchParams.append(
                                        ("specialization_slug", "=", specialization)
                                    )
                                    segment = 7
        # Requête
        programs = (
            request.env["school.program"]
            .sudo()
            .search(
                searchParams,
                order="year_short_name ASC, domain_name ASC, cycle_sequence ASC, cycle_subtype ASC, name ASC",
            )
        )

        # Si un seul résultat
        if len(programs) == 1:
            # Si la route ne correspond pas à celle du programme : redirection
            return request.redirect("/programme/" + slug(programs[0]))
        # Si plusieurs résultats
        elif len(programs) > 1:
            # Génération des options
            options = self._get_options(programs, segment)
            # S'il n'y a qu'une option disponible, on la sélectionne de suite.
            if len(options) == 1 and options[0] != "-":
                return request.redirect(options[0]["uri"])
            if options.count("-"):
                options.remove("-")
            # Génération du breadcrump
            breadcrumb = self._get_breadcrumb(programs[0], segment)
            # Données pour le rendu
            template = "website_school_management.programmes_liste"
            values = {
                "main_object": programs,
                "program_list": programs,
                "breadcrumb": breadcrumb,
                "options": options,
            }
            return request.render(template, values)
        # Si 0 résultat
        else:
            return Response(template="website.page_404", status=404)

    @http.route(
        ["/programme/<string:program_slug>"],
        type="http",
        auth="public",
        website=True,
        sitemap=_sitemap_programs,
    )
    def programme(self, program_slug, redirect=None, **post):
        _, program_id = unslug(program_slug)
        program = (
            request.env["school.program"]
            .sudo()
            .search([("state", "=", "published"), ("id", "=", program_id)])
        )
        if program:
            # Préparation du breadcrump
            breadcrumb = self._get_breadcrumb(program, 7)
            template = "website_school_management.programme_fiche"
            values = {
                "main_object": program,
                "program": program,
                "breadcrumb": breadcrumb,
            }
            return request.render(template, values)
        else:
            return Response(template="website.page_404", status=404)

    ##############
    # TEMPORAIRE #
    ##############

    # Gestion de la génération du PDF d'un programme de cours
    @http.route(
        "/impression_programme/<string:program_slug>",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def print_program_pdf(self, program_slug, **kw):
        _, program_id = unslug(program_slug)
        program = (
            request.env["school.program"]
            .sudo()
            .search([("state", "=", "published"), ("id", "=", program_id)])
        )
        if program:
            pdf = request.env.ref(
                "website_school_management.action_impression_programme_id"
            )._render_qweb_pdf(
                "website_school_management.action_impression_programme_id", [program.id]
            )[
                0
            ]
            pdfhttpheaders = [
                ("Content-Type", "application/pdf"),
                ("Content-Length", "%s" % len(pdf)),
            ]
            return http.request.make_response(pdf, headers=pdfhttpheaders)
        else:
            return Response(template="website.page_404", status=404)

    # Gestion de la route d'un cours
    @http.route(
        ["/cours/<string:course_slug>"],
        type="http",
        auth="public",
        website=True,
        sitemap=True,
    )
    def cours(self, course_slug, redirect=None, **post):
        _, course_id = unslug(course_slug)
        course = request.env["school.course"].sudo().search([("id", "=", course_id)])
        if course:
            values = {
                "main_object": course,
                "course": course,
            }
            return request.render("website_school_management.cours_fiche", values)
        else:
            return Response(template="website.page_404", status=404)

    @http.route("/cours/cours_demande_description", type="json", auth="public")
    def request_details_cours(self, **post):
        course_id = post.get("course_id")
        course = request.env["school.course"].sudo().search([("id", "=", course_id)])
        if course:
            emailResponsible = course.course_group_id.responsible_id.email
            email = post.get("email")
            first_name = post.get("first_name")
            last_name = post.get("last_name")
            if email and first_name and last_name:
                vals = {
                    "emailObject": "Demande de description de cours",
                    "emailResponsible": emailResponsible,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "course": course,
                    "url": request.httprequest.url_root + "cours/" + slug(course),
                }
                self.send_email(vals)
                return {"result": "success"}
        return {"result": "failure"}

    def send_email(self, vals):
        mail_body = request.env["ir.qweb"]._render(
            "website_school_management.cours_details_request", vals
        )

        mail = (
            request.env["mail.mail"]
            .sudo()
            .create(
                {
                    "subject": vals["emailObject"],
                    "email_from": "no-reply@horizon.com",
                    "author_id": request.env.user.partner_id.id,
                    "email_to": vals["emailResponsible"],
                    "body_html": mail_body,
                }
            )
        )
        mail.send()
